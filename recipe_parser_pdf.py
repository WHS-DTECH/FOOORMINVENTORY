"""Recipe parser for extracting recipes from PDF documents."""

import re

def parse_recipes_from_text(text):
    """
    Parse recipes from PDF text that contain Ingredients, Equipment, and Method sections.

    This version is tolerant of trailing spaces, wrapped lines (equipment lists
    that continue on the next line), and repeated section headers.
    """
    recipes = []
    # --- Improved: Extract lines matching 'Making Activity :' and real recipe headings ---
    # Use 'Making Activity :' to help identify recipe titles, but continue parsing for details
    making_activity_indices = []
    making_activity_pattern = re.compile(r'Making Activity\s*:\s*(.+)', re.I)
    lines = text.split('\n')
    for idx, line in enumerate(lines):
        match = making_activity_pattern.search(line)
        if match:
            making_activity_indices.append((idx, match.group(1).strip()))
    import unicodedata
    def normalize_line(s):
        # Normalize unicode quotes/dashes to ASCII
        replacements = {
            '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
            '\u2013': '-', '\u2014': '-', '\u2212': '-',
        }
        for k, v in replacements.items():
            s = s.replace(k, v)
        # Normalize unicode to NFKC
        s = unicodedata.normalize('NFKC', s)
        # Remove non-printable characters
        s = ''.join(c for c in s if c.isprintable())
        return s


    # --- Global Filtering: Remove blank pages, repeated headers/footers, and known non-recipe lines ---
    def is_junk_line(line):
        junk_patterns = [
            r'^\s*$',  # blank line
            r'^page \d+',  # page numbers
            r'^(food technology|assessment|evaluation|scenario|brief|attributes|learning objective|copyright|school name|westland high school)',
            r'^\d{1,3}$',  # single numbers (page numbers)
            r'^(recipe book setup|recipe index|admin|shopping list|class ingredients|food room)',
            r'^\W+$',  # lines with only non-word chars
        ]
        for pat in junk_patterns:
            if re.match(pat, line.strip(), re.I):
                return True
        return False

    # Normalize all lines and filter out junk lines
    lines = [normalize_line(line) for line in text.split('\n')]
    # Remove repeated headers/footers and junk lines
    filtered_lines = []
    seen_lines = set()
    for line in lines:
        norm = line.strip().lower()
        if is_junk_line(line):
            continue
        # Remove repeated lines (headers/footers)
        if norm and norm in seen_lines:
            continue
        seen_lines.add(norm)
        filtered_lines.append(line)
    lines = filtered_lines

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

    # --- Advanced Title Detection ---
    # Try to use spaCy for NLP-based title detection if available
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
    except Exception:
        nlp = None

    def is_likely_title(line, prev_line=None, font_size=None, is_bold=None):
        # Heuristics: not a section header, not all lowercase, not too short, not junk
        if not line or len(line) < 4:
            return False
        if detect_section(line):
            return False
        if line.islower():
            return False
        if re.match(r'^[\d\W]+$', line):
            return False
        # If font size or boldness is available, prefer larger/bold lines
        if font_size is not None and font_size < 10:
            return False
        if is_bold is not None and not is_bold:
            return False
        # Use NLP to check if line is a noun phrase or title
        if nlp:
            doc = nlp(line)
            if any(ent.label_ == 'WORK_OF_ART' for ent in doc.ents):
                return True
            # If the line is a single noun chunk, likely a title
            if len(list(doc.noun_chunks)) == 1 and len(line.split()) < 10:
                return True
        # Fallback: Title case and not a known junk line
        if line[0].isupper() and not any(x in line.lower() for x in ['skills', 'worksheet', 'target', 'tick', 'review', 'technology', 'assessment', 'evaluation', 'scenario', 'brief', 'attributes', 'learning objective']):
            return True
        return False

    # Track extra fields
    extra_fields = {"notes": [], "tips": [], "prep_time": None, "serving_size": None}



    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        line_lower = line.lower()

        # --- Advanced Recipe Title and Serving Size Extraction ---
        # Try to use advanced heuristics and NLP for title detection
        if not recipe_data and is_likely_title(line):
            # Try to extract serving size from the line
            title_match = re.match(r'^(.*?)(?:\s*\(per group of (\d+)\))?(?:\s*serves\s*(\d+))?$', line, re.I)
            title_candidate = title_match.group(1).strip() if title_match else line.strip()
            serves_candidate = title_match.group(2) or title_match.group(3) if title_match else None
            # Save previous recipe if complete
            if recipe_data and (recipe_data.get('ingredients') or recipe_data.get('method')):
                recipes.append(format_recipe(recipe_data, extra_fields))
            recipe_data = {'name': title_candidate, 'ingredients': [], 'equipment': [], 'method': []}
            # Reset extra_fields for each new recipe
            extra_fields = {"notes": [], "tips": [], "prep_time": None, "serving_size": None}
            if serves_candidate:
                extra_fields['serving_size'] = serves_candidate
            current_section = None
            # Warn if the title is ambiguous (e.g., very short or generic)
            if len(title_candidate.split()) < 2:
                parse_warnings.append(f"Ambiguous recipe title detected: '{title_candidate}' on line {i+1}")
            i += 1
            continue

        # Recipe title marker: support more formats (e.g., 'Recipe:', all caps, etc.)
        if (re.match(r'^(making activity|recipe)\s*:', line_lower)):
            # save previous recipe if complete
            if recipe_data and (recipe_data.get('ingredients') or recipe_data.get('method')):
                recipes.append(format_recipe(recipe_data, extra_fields))
            # start new recipe
            recipe_name = re.sub(r'^(making activity|recipe)\s*:', '', raw, flags=re.I).strip()
            # Remove leading/trailing colons and whitespace, and strip 'Recipe:' if present
            recipe_name = recipe_name.lstrip(':').strip()
            recipe_name = re.sub(r'^recipe\s*:?\s*', '', recipe_name, flags=re.I).strip()
            # Try to extract serving size from the name
            serves_match = re.search(r'(.*?)(?:\s*\(per group of (\d+)\))?(?:\s*serves\s*(\d+))?$', recipe_name, re.I)
            if serves_match:
                recipe_name_clean = serves_match.group(1).strip()
                serves_candidate = serves_match.group(2) or serves_match.group(3)
            else:
                recipe_name_clean = recipe_name
                serves_candidate = None
            recipe_data = {'name': recipe_name_clean, 'ingredients': [], 'equipment': [], 'method': []}
            # Reset extra_fields for each new recipe
            extra_fields = {"notes": [], "tips": [], "prep_time": None, "serving_size": None}
            if serves_candidate:
                extra_fields['serving_size'] = serves_candidate
            current_section = None
            i += 1
            continue

        # All-caps line (likely a title) if not in a section and not junk
        if not recipe_data and line and line.isupper() and 3 < len(line) < 80 and not any(x in line_lower for x in ['learning objective', 'page ', 'food technology', 'assessment', 'evaluation', 'scenario:', 'brief:', 'attributes:']):
            # Remove 'Recipe:' from all-caps lines
            name = re.sub(r'^recipe\s*:?\s*', '', line, flags=re.I).strip().title()
            # Try to extract serving size from the name
            serves_match = re.search(r'(.*?)(?:\s*\(per group of (\d+)\))?(?:\s*serves\s*(\d+))?$', name, re.I)
            if serves_match:
                name_clean = serves_match.group(1).strip()
                serves_candidate = serves_match.group(2) or serves_match.group(3)
            else:
                name_clean = name
                serves_candidate = None
            recipe_data = {'name': name_clean, 'ingredients': [], 'equipment': [], 'method': []}
            if serves_candidate:
                extra_fields['serving_size'] = serves_candidate
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

        # Detect and collect notes, tips, prep time, serving size
        if 'note:' in line_lower or 'notes:' in line_lower:
            extra_fields['notes'].append(line)
            i += 1
            continue
        if 'tip:' in line_lower or 'tips:' in line_lower:
            extra_fields['tips'].append(line)
            i += 1
            continue
        if 'prep time' in line_lower:
            # Extract time value
            match = re.search(r'prep time\s*[:\-]?\s*(\d+\s*\w+)', line_lower)
            if match:
                extra_fields['prep_time'] = match.group(1)
            i += 1
            continue
        if 'serves' in line_lower or 'serving size' in line_lower:
            match = re.search(r'(serves|serving size)\s*[:\-]?\s*(\d+)', line_lower)
            if match:
                extra_fields['serving_size'] = match.group(2)
            i += 1
            continue

        # End markers
        if any(marker in line_lower for marker in ['top tips', 'skills', 'evaluation', 'assessment']):
            # accept recipes that have ingredients and method (equipment optional)
            if recipe_data.get('ingredients') and recipe_data.get('method'):
                recipes.append(format_recipe(recipe_data, extra_fields))
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
        recipes.append(format_recipe(recipe_data, extra_fields))

    # Optionally return warnings/errors for user review
    if parse_warnings:
        return {"recipes": recipes, "warnings": parse_warnings}
    return recipes


def format_recipe(recipe_data, extra_fields=None):
    """Format parsed recipe data into structured format for database, with optional extra fields."""
    # Parse ingredients into structured format
    ingredients = []
    for ing_line in recipe_data.get('ingredients', []):
        ing_line = ing_line.strip()
        if ing_line:
            # Remove leading bullet or dash
            ing_line = re.sub(r'^[•\-]\s*', '', ing_line)
            # Remove leading numbers (e.g., '1. ')
            ing_line = re.sub(r'^\d+\.\s*', '', ing_line)
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
    # Split by lines that start with a number, bullet, or dash (no look-behind)
    method_steps = []
    step_pattern = re.compile(r'^(\d+\.|-|•)\s+', re.MULTILINE)
    buffer = ''
    for line in method_lines:
        if step_pattern.match(line):
            if buffer:
                method_steps.append(buffer.strip())
            buffer = step_pattern.sub('', line, count=1)
        else:
            if buffer:
                buffer += ' ' + line.strip()
            else:
                buffer = line.strip()
    if buffer:
        method_steps.append(buffer.strip())
    if method_steps:
        method_text = '\n'.join(method_steps)

    # Add extra fields if present
    result = {
        'name': recipe_data.get('name', 'Unknown Recipe').strip(),
        'ingredients': ingredients,
        'equipment': equipment,
        'method': method_text,
        'serving_size': None
    }
    if extra_fields:
        if extra_fields.get('serving_size'):
            result['serving_size'] = extra_fields['serving_size']
        if extra_fields.get('prep_time'):
            result['prep_time'] = extra_fields['prep_time']
        if extra_fields.get('notes'):
            result['notes'] = extra_fields['notes']
        if extra_fields.get('tips'):
            result['tips'] = extra_fields['tips']
    return result


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
        # Always use all words after quantity and unit as ingredient
        if unit:
            # Tokenize line and reconstruct ingredient
            tokens = line.split()
            q_tokens = len(quantity_raw.split()) if quantity_raw else 0
            u_tokens = len(unit.split()) if unit else 0
            ingredient_tokens = tokens[q_tokens + u_tokens:]
            ingredient = ' '.join(ingredient_tokens).strip()
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
