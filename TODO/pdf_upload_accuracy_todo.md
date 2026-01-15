# TODO: Recommendations for Maximum Accuracy – PDF Upload

1. **Improve PDF parser robustness**
   - Ensure the parser reliably skips preamble/non-recipe text and always detects the first real recipe title.
   - Confirm accurate extraction of serving sizes, even with format variations.
   - Add logic to ignore blank pages, headers, or footers.

2. **Implement duplicate recipe detection**
   - Before inserting a new recipe, check if a recipe with the same name (and possibly ingredients) already exists to avoid accidental duplicates, especially on re-upload.

3. **Enhance error reporting for PDF upload**
   - Ensure the upload process provides clear feedback if a recipe fails to parse or insert, so issues can be quickly identified and fixed.

4. **Verify provenance tracking for PDF uploads**
   - Confirm every recipe inserted via PDF upload is correctly linked in the `recipe_upload` table, with accurate source details (file name, user).

5. **Wrap PDF upload in bulk transaction**
   - If uploading multiple recipes from one PDF, wrap the inserts in a transaction so that a failure in one recipe doesn’t leave the database in a partial state.

6. **Add logging for PDF upload process**
   - Add logging for each recipe processed, including successes and failures, to help with debugging and audit trails.
