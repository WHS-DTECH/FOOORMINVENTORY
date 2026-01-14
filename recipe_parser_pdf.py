"""Recipe parser for extracting recipes from PDF documents."""

import re

def parse_recipes_from_text(text):
    """
    Parse recipes from PDF text that contain Ingredients, Equipment, and Method sections.

    This version is tolerant of trailing spaces, wrapped lines (equipment lists
    that continue on the next line), and repeated section headers.
    """
    recipes = []
    lines = text.split('\n')

    recipe_data = None
    current_section = None
    # Collect warnings/errors for user review
    parse_warnings = []

    i = 0
    # Section header regex patterns (flexible, supports typos and alternatives)
    section_patterns = {
        'ingredients': re.compile(r'\b(ingredien[ct]s?|ingredi[ae]nts?)\b', re.I),
        'equipment': re.compile(r'\b(equipm[ea]nt|tools?)\b', re.I),
        'method': re.compile(r'\b(meth[oa]d|steps?|instructions?)\b', re.I),
    }
    # Acceptable section header alternatives/typos
    def detect_section(line):
        for section, pattern in section_patterns.items():
            if pattern.search(line):
                return section
        return None

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        line_lower = line.lower()


        # Recipe title marker: support more formats (e.g., 'Recipe:', all caps, etc.)
        title_match = None
        # Try 'Making Activity :' or 'Recipe :' or 'Recipe:'
        if (re.match(r'^(making activity|recipe)\s*:', line_lower)):
            # save previous recipe if complete
            if recipe_data and recipe_data.get('ingredients') and recipe_data.get('equipment') and recipe_data.get('method'):
                recipes.append(format_recipe(recipe_data))

            # start new recipe
            recipe_name = re.sub(r'^(making activity|recipe)\s*:', '', raw, flags=re.I).strip()
            recipe_data = {'name': recipe_name, 'ingredients': [], 'equipment': [], 'method': []}
            current_section = None
            i += 1
            continue

        # All-caps line (likely a title) if not in a section and not junk
        if not recipe_data and line and line.isupper() and 3 < len(line) < 80 and not any(x in line_lower for x in ['learning objective', 'page ', 'food technology', 'assessment', 'evaluation', 'scenario:', 'brief:', 'attributes:']):
            recipe_data = {'name': line.title(), 'ingredients': [], 'equipment': [], 'method': []}
            current_section = None
            i += 1
            continue

        # If no recipe started yet, try to infer one from an ingredient line
        if not recipe_data:
            # simple ingredient detection: starts with a number or contains common units
            ll = line.lower()
            def looks_like_ingredient(s):
                if not s:
                    return False
                # Skip single page numbers (1-3 digits alone)
                if s.strip().isdigit() and len(s.strip()) <= 3:
                    return False
                if s[0].isdigit():
                    return True
                for token in ['g ', 'ml', 'cup', 'tsp', 'tbsp', 'tablespoon', 'teaspoon', 'slice', 'large', 'small', 'packet', 'can']:
                    if token in s:
                        return True
                if s.startswith('•'):
                    return True
                return False

            if looks_like_ingredient(ll):
                # Look back for a plausible title within previous 15 lines
                # Collect all non-junk lines, then pick the best title candidate
                candidates = []
                for j in range(1, 15):
                    idx = i - j
                    if idx < 0:
                        break
                    cand = lines[idx].strip()
                    low = cand.lower()
                    
                    if not cand:
                        continue
                    
                    # Skip obvious junk
                    if low.isdigit():
                        continue
                    if any(k in low for k in ['learning objective', 'page ', 'food technology', 'assessment', 'evaluation', 'scenario:', 'brief:', 'attributes:']):
                        continue
                    
                    # Check if it's an ingredient line (stop looking back)
                    def _looks_like_ingredient(s):
                        if not s:
                            return False
                        if s[0].isdigit():
                            return True
                        for token in ['g ', 'ml', 'cup', 'tsp', 'tbsp', 'tablespoon', 'teaspoon', 'slice']:
                            if token in s:
                                return True
                        if s.startswith('•'):
                            return True
                        return False
                    
                    if _looks_like_ingredient(low):
                        break
                    
                    # Add to candidates
                    candidates.append(cand)
                
                # Find best title from candidates
                title = None
                for cand in candidates:
                    low = cand.lower()
                    # Skip section headers like "Week 9 :" 
                    if 'week ' in low and ':' in cand:
                        continue
                    # Skip continuation lines that aren't real titles
                    if cand.startswith(('group of', ')', 'work in pairs')):
                        continue
                    # Prefer lines that look like recipe names (not too long, no excessive punctuation)
                    if 3 < len(cand) < 100 and cand.count('.') < 3:
                        # This looks like a good title
                        title = cand
                        break
                
                if title:
                    # Clean up title - remove common prefixes/suffixes
                    title = re.sub(r'\(per.*$', '', title).strip()  # Remove "(per..." to end
                    title = re.sub(r'\(makes \d+ .*?\)', '', title, flags=re.I).strip()
                    title = re.sub(r'–\s*work in pairs', '', title, flags=re.I).strip()
                else:
                    # Use filename as fallback if available, else placeholder
                    title = 'Unknown Recipe'
                recipe_data = {'name': title, 'ingredients': [], 'equipment': [], 'method': []}
                current_section = 'ingredients'
                # fall through to collect this ingredient line
            else:
                # Log unassigned line as warning
                parse_warnings.append(f"Unassigned line (no recipe started): '{line}' at line {i+1}")
                i += 1
                continue


        # Section header detection using regex (flexible, supports typos/alternatives)
        section = detect_section(line_lower)
        if section:
            # If we have no recipe started yet but hit a section, look back for a title
            if not recipe_data or not recipe_data.get('name'):
                title = None
                for j in range(1, 10):
                    idx = i - j
                    if idx < 0:
                        break
                    cand = lines[idx].strip()
                    if cand and len(cand) > 3 and len(cand) < 100:
                        low = cand.lower()
                        # Skip headers and junk
                        if not any(skip in low for skip in ['learning objective', 'keywords', 'ingredients', 'equipment', 'method', 'week ', 'page ', 'food technology', 'by the end']):
                            title = cand
                            break
                if title and not recipe_data:
                    recipe_data = {'name': title, 'ingredients': [], 'equipment': [], 'method': []}
            current_section = section
            i += 1
            continue

        # End markers
        if any(marker in line_lower for marker in ['top tips', 'skills', 'evaluation', 'assessment']):
            # accept recipes that have ingredients and method (equipment optional)
            if recipe_data.get('ingredients') and recipe_data.get('method'):
                recipes.append(format_recipe(recipe_data))
            recipe_data = None
            current_section = None
            i += 1
            continue

        # Collect content: join wrapped equipment lines if necessary
        if current_section:
            if not line:
                i += 1
                continue
            # Remove bullet markers
            if line.startswith('•'):
                line = line[1:].strip()

            # If equipment line contains commas and may be wrapped, try to merge
            if current_section == 'equipment':
                # If previous equipment entry looks like a continuation (no comma and ends with a word), append
                if recipe_data['equipment'] and not recipe_data['equipment'][-1].endswith(',') and not recipe_data['equipment'][-1].endswith('.') and not recipe_data['equipment'][-1].endswith(':'):
                    # append as continuation
                    recipe_data['equipment'][-1] = recipe_data['equipment'][-1] + ' ' + line
                else:
                    recipe_data['equipment'].append(line)
            else:
                recipe_data[current_section].append(line)
        else:
            # Log unassigned line (not in any section)
            if line:
                parse_warnings.append(f"Unassigned line (not in any section): '{line}' at line {i+1}")

        i += 1

    # final recipe
    if recipe_data and recipe_data.get('ingredients') and recipe_data.get('method'):
        recipes.append(format_recipe(recipe_data))

    # Optionally return warnings/errors for user review
    if parse_warnings:
        return {"recipes": recipes, "warnings": parse_warnings}
    return recipes


def format_recipe(recipe_data):
    """Format parsed recipe data into structured format for database."""
    # Parse ingredients into structured format
    ingredients = []
    for ing_line in recipe_data.get('ingredients', []):
        ing_line = ing_line.strip()
        if ing_line:
            ingredients.append(parse_ingredient_line(ing_line))

    # Parse equipment into list (split by comma, semicolon, or newline)
    equipment_text = '\n'.join(recipe_data.get('equipment', []))
    equipment = []
    for line in equipment_text.split('\n'):
        # Split on commas and semicolons
        for item in re.split(r'[;,]', line):
            item = item.strip()
            if item:
                equipment.append(item)
    if not equipment:
        # Try splitting by space if no commas/semicolons
        equipment = [e.strip() for e in equipment_text.split() if e.strip()]

    # Parse method - split steps by numbers or bullet points
    method_lines = recipe_data.get('method', [])
    method_text = '\n'.join(method_lines)
    # Split by lines that start with a number, bullet, or dash
    method_steps = []
    for line in method_lines:
        # Match lines like '1. Do this', '- Do that', '• Do something'
        steps = re.split(r'(?<=\n|^)(?:\d+\.|\-|•)\s+', line)
        for step in steps:
            step = step.strip()
            if step:
                method_steps.append(step)
    if method_steps:
        method_text = '\n'.join(method_steps)

    return {
        'name': recipe_data.get('name', 'Unknown Recipe').strip(),
        'ingredients': ingredients,
        'equipment': equipment,
        'method': method_text,
        'serving_size': None
    }


def parse_ingredient_line(line):
    """Parse a single ingredient line into quantity, unit, and ingredient name.
    Handles fractions, ranges, multi-word units, and uses regex for extraction."""
    import fractions
    line = line.strip()
    if not line:
        return {"quantity": "", "unit": "", "ingredient": ""}

    # Regex for quantity (supports fractions, ranges, decimals)
    quantity_pattern = r'^(\d+[\d\s\/\.-]*|[¼½¾⅓⅔⅛⅜⅝⅞])'
    unit_pattern = r'(g|gram|grams|kg|ml|l|litre|litres|cup|cups|tsp|tbsp|tablespoon|teaspoon|slice|slices|pinch|packet|can|large|small|clove|cloves|piece|pieces|stick|sticks|oz|pound|lb|dash|drop|drops|bunch|bunches|handful|handfuls|cm|mm|inch|inches|sheet|sheets|fillet|fillets|filet|filets|strip|strips|cube|cubes|sprig|sprigs|leaf|leaves|head|heads|jar|jars|bottle|bottles|container|containers|pack|packs|bag|bags|dozen|quart|pint|gal|gallon|liters|milliliter|millilitre|milliliters|millilitres|tablespoons|teaspoons|tablespoonful|teaspoonful|tablespoonfuls|teaspoonfuls|dash|dashes|drop|drops|bunch|bunches|handful|handfuls|pinch|pinches|slice|slices|piece|pieces|clove|cloves|can|cans|packet|packets|stick|sticks|sheet|sheets|fillet|fillets|filet|filets|strip|strips|cube|cubes|sprig|sprigs|leaf|leaves|head|heads|jar|jars|bottle|bottles|container|containers|pack|packs|bag|bags|dozen|quart|pint|gal|gallon|liters|milliliter|millilitre|milliliters|millilitres|tablespoons|teaspoons|tablespoonful|teaspoonful|tablespoonfuls|teaspoonfuls)?'
    # Full pattern: quantity [unit] ingredient
    pattern = re.compile(rf'\s*({quantity_pattern})\s*({unit_pattern})?\s*(.*)', re.I)

    match = pattern.match(line)
    if match:
        quantity_raw = match.group(1) or ""
        unit = (match.group(2) or "").strip()
        ingredient = (match.group(3) or "").strip()
        # Normalize quantity (handle fractions and ranges)
        quantity = quantity_raw.strip()
        # Convert unicode fractions to float
        unicode_fractions = {
            '¼': 0.25, '½': 0.5, '¾': 0.75, '⅓': 1/3, '⅔': 2/3, '⅛': 1/8, '⅜': 3/8, '⅝': 5/8, '⅞': 7/8
        }
        for uf, val in unicode_fractions.items():
            if uf in quantity:
                quantity = str(val)
        # Handle ranges (e.g., 2-3)
        if '-' in quantity:
            quantity = quantity.split('-')[0].strip()
        # Handle fractions (e.g., 1 1/2)
        try:
            if '/' in quantity:
                parts = quantity.split()
                if len(parts) == 2:
                    whole = int(parts[0])
                    frac = float(fractions.Fraction(parts[1]))
                    quantity = str(whole + frac)
                else:
                    quantity = str(float(fractions.Fraction(quantity)))
        except Exception:
            pass
        return {"quantity": quantity, "unit": unit, "ingredient": ingredient}
    # If no match, treat whole line as ingredient
    return {"quantity": "", "unit": "", "ingredient": line}
