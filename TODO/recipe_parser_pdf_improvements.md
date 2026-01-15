# TODO: Improvements for recipe_parser_pdf.py

1. **Improve section header detection**
   - Use regex for flexible matching of section headers (Ingredients, Equipment, Method).
   - Support alternative names and typos.

2. **Expand recipe title detection**
   - Handle more title formats (e.g., 'Recipe:', all caps, etc.).
   - Use filename or placeholder if not found.

3. **Enhance ingredient parsing**
   - Handle fractions, ranges, multi-word units.
   - Use regex for quantity/unit/ingredient extraction.
   - Consider advanced parsing libraries (e.g., ingredient-phrase-tagger).

4. **Improve equipment and method parsing**
   - Split equipment on semicolons/newlines, not just commas.
   - For method, split steps by numbers or bullet points for better structure.

5. **Add error handling and logging**
   - Log lines that can't be parsed or assigned.
   - Optionally collect and return warnings/errors for user review.

6. **Normalize unicode and encoding**
   - Normalize unicode (quotes, dashes) to ASCII.
   - Strip non-printable characters.

7. **Expand output structure**
   - Add optional fields for notes, tips, serving size, prep time, etc., if detected in the text.

8. **Add unit tests for edge cases**
   - Test missing sections, unusual formatting, multi-recipe PDFs, and other edge cases.
