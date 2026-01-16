# Recipe PDF Parsing TODO (as of 2026-01-15)

## Current Status
- PDF upload, two-step confirmation, and session storage are working.
- Debug logging added: PDF text and detected recipes are printed to logs.
- Current parser extracts a lot of worksheet/non-recipe content as recipes.
- Actual recipes (e.g., Fruit Smoothie, Muffins, Couscous, Crumble) are not reliably detected as recipe blocks.
- Ingredient detection is too strict for your document format.

## Next Steps (Recommended Improvements)
1. **Block-Based Parsing:**
   - Use every line matching `Making Activity : <title>` as the start of a new recipe block.
   - Collect all lines until the next `Making Activity :` or end of file as that recipe’s block.
2. **Section Extraction:**
   - Within each block, look for `Ingredients`, `Equipment`, and `Method` headers.
   - Collect lines under each header until the next header or end of block.
3. **Loosen Ingredient Detection:**
   - Accept any line under `Ingredients` as an ingredient, not just those with numbers/units.
4. **Remove Debug Logging** after parser is working reliably.

## Reference
- See debug output in Render logs for extracted text and current parser output.
- Attachments in chat show real PDF structure and expected recipe blocks.

---
**Next action:** Refactor parser to use block-based logic as above for robust recipe extraction.

# Recipe PDF Parsing TODO (as of 2026-01-16)

## ✅ Completed (2026-01-16)
- Implemented two-sweep parsing approach:
  - **Sweep 1:** Page-level extraction to identify recipe pages by "Making Activity :" marker
  - **Sweep 2:** Detailed parsing only on identified recipe pages
- Added pattern-based ingredient filtering (number + unit + item)
- Reports actual page numbers (page count, not printed page numbers)
- Added comprehensive logging for debugging

## Current Implementation
- `identify_recipe_pages()`: Scans all pages for recipe markers
- `parse_recipe_details()`: Extracts ingredients, equipment, method from recipe pages only
- `filter_ingredients()`: Uses regex to validate ingredient format
- Reduces false positives from teaching notes and worksheets

## Next Steps
1. **Test with actual PDF files** to verify recipe detection accuracy
2. **Fine-tune ingredient pattern** if needed based on test results
3. **Handle multi-page recipes** if recipes span multiple pages
4. **Remove old debug logging** once confirmed working

## Reference
- Two-sweep approach eliminates non-recipe content before detailed parsing
- Page numbers reported as actual page count for debugging
