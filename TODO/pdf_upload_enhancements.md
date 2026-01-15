# PDF Recipe Upload Accuracy Enhancements

1. Improve Title Detection
   - Use advanced NLP or regex to better identify recipe titles (font size, boldness, title patterns).
   - Allow manual correction of detected titles in the preview modal.

2. Page Range Selection
   - Let users specify which pages to scan or ignore, especially if the PDF has non-recipe content.

3. Ingredient & Instruction Extraction
   - Highlight and preview extracted ingredients/instructions for each recipe before upload.
   - Allow users to edit or correct extracted content in the preview.

4. Duplicate & Similarity Checks
   - Warn if a recipe with a similar name or content already exists in the database.

5. Error Feedback Loop
   - Store user feedback on missing/misidentified recipes and use it to retrain or refine extraction logic.

6. Multi-language & OCR Support
   - If PDFs are scanned images, integrate OCR (like Tesseract) for text extraction.
   - Support for accented characters or other languages if needed.

7. Logging & Analytics
   - Track which extraction rules fail most often and which recipes are most frequently flagged, to guide future improvements.
