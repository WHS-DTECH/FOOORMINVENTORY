"""
Debug logic for the Title field in the parser debug workflow.
"""


# --- Title Detection Logic (copied for debug use, do not edit recipe_parser_pdf.py) ---
import re
try:
    import spacy
    nlp = spacy.load('en_core_web_sm')
except Exception:
    nlp = None

def is_likely_title(line, prev_line=None, font_size=None, is_bold=None, detect_section=None):
    # Heuristics: not a section header, not all lowercase, not too short, not junk
    if not line or len(line) < 4:
        return False
    if detect_section and detect_section(line):
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
    if line[0].isupper() and not any(x in line.lower() for x in [
        'skills', 'worksheet', 'target', 'tick', 'review', 'technology', 'assessment', 'evaluation', 'scenario', 'brief', 'attributes', 'learning objective']):
        return True
    return False

def infer_title_above(lines, start_idx, ingredient_block):
    # Look up to 5 lines above the first ingredient line
    food_words = set()
    for ing in ingredient_block:
        tokens = ing.split()
        if len(tokens) > 2:
            food_words.add(tokens[-1].lower())
            food_words.add(tokens[2].lower())
    for j in range(1, 6):
        idx = start_idx - j
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if 2 < len(candidate) < 60:
            if any(word in candidate.lower() for word in food_words):
                return candidate
    for j in range(1, 6):
        idx = start_idx - j
        if idx < 0:
            break
        candidate = lines[idx].strip()
        if 2 < len(candidate) < 60:
            return candidate
    return 'Unknown Recipe'

def debug_title(raw_title, test_recipe_id):
    # You can now use is_likely_title and infer_title_above for debugging
    return raw_title
