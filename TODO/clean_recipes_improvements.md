# TODO: Improvements for clean_recipes.py

1. **Make database path configurable**
   - Allow passing the database path as a command-line argument for flexibility.

2. **Refine regex patterns**
   - Use word boundaries and more precise patterns for junk recipe detection.

3. **Switch to logging module**
   - Replace print statements with Python's logging module for better log control and levels.

4. **Add unit tests**
   - Write tests for each function using an in-memory SQLite database to ensure correctness.

5. **Optimize for large databases**
   - Use batch deletes/updates or explicit transactions for better performance on large datasets.

6. **Support custom rules/config**
   - Allow passing custom junk/duplicate rules via a config file or command-line arguments for extensibility.

7. **Add error handling**
   - Use try/except blocks around database operations to handle and report errors gracefully.

8. **Expand docstrings**
   - Document expected schema, function side effects, and usage examples in the docstrings.
