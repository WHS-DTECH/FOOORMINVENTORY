# Flask app.py Best Practice Refactor TODO

## Goals
- Avoid repetitive errors from misplaced code (e.g., app or blueprint buried below route definitions)
- Ensure maintainability and clarity for all contributors
- Align with Flask and Python best practices

## Best Practice Layout Checklist

1. **All Imports at the Top**
   - Standard library imports
   - Third-party imports
   - Local imports
2. **App/Blueprint Creation and Configuration**
   - `app = Flask(__name__)`
   - `app.config` and environment setup
   - Blueprint registration
   - Flask-Login, database, and other extension setup
3. **Utility Functions and Filters**
   - Helper functions (e.g., get_db_connection, format_nz_week)
   - Jinja filters
4. **Error Handlers**
   - Custom error pages (404, 500, etc.)
5. **Route Definitions**
   - Grouped by feature/module (auth, admin, recipes, etc.)
   - Use Blueprints for large apps
6. **Main Entrypoint**
   - `if __name__ == "__main__": app.run()`
7. **Docstrings and Type Hints**
   - All functions and routes should have docstrings
   - Use type hints where possible
8. **Remove Redundant/Commented Code**
   - No commented-out or duplicate code blocks
9. **Consistent Naming and Style**
   - snake_case for functions/variables, PascalCase for classes
   - PEP8 compliance

## Action Items
- [ ] Move all imports to the top
- [ ] Move app creation/config to the top (after imports)
- [ ] Register blueprints/extensions immediately after app creation
- [ ] Move utility functions below config
- [ ] Add error handlers section
- [ ] Group routes by feature/module
- [ ] Add main entrypoint at the end
- [ ] Add/verify docstrings and type hints
- [ ] Remove redundant/commented code
- [ ] Enforce consistent naming and style

---

**From now on, all new code and patches should follow this structure.**
