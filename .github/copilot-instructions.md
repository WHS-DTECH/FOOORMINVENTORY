# Food Room Inventory - AI Coding Agent Instructions

## Project Overview
Flask web application for managing school food technology recipes, class bookings, and shopping lists with Google OAuth authentication and role-based access control.

## Architecture & Key Components

### Authentication & Authorization
- **Google OAuth 2.0** via `auth.py` and `google-auth-oauthlib`
- **Role-based access control** using `@require_role()` decorators from `auth.py`
- **Four permission levels**: VP (admin), DK (teachers), MU (booking staff), public (unauthenticated)
- **Staff lookup**: Users authenticated via Google are matched to staff records in `teachers` table by email
- **User model**: Flask-Login with `User` class storing `staff_code`, `role`, and `additional_roles`

### Database (SQLite)
- **Single file**: `recipes.db` (gitignored)
- **Initialize**: Run `python setup_database.py` to create schema and default permissions
- **Key tables**: `recipes`, `teachers`, `classes`, `class_bookings`, `role_permissions`, `user_roles`, `recipe_suggestions`
- **Schema convention**: JSON fields stored as TEXT (use `json.dumps()`/`json.loads()`)
- **Ingredients format**: Array of `{"quantity": str, "unit": str, "ingredient": str}` dictionaries

### Recipe Parsing (`recipe_parser.py`)
- **PDF extraction**: Uses PyPDF2 to extract full text, then `parse_recipes_from_text()` to identify recipe blocks
- **Expected sections**: "Making Activity : Name", "Ingredients", "Equipment", "Method"
- **Ingredient parsing**: `parse_ingredient_line()` extracts quantity, unit, ingredient from text like "100 g flour"
- **Tolerance**: Handles wrapped lines, trailing spaces, repeated headers, no section header (infers from content)

## Developer Workflows

### Starting the App
```bash
python app.py                    # Runs on localhost:5000 with debug=True
# Requires .env file with GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FLASK_SECRET_KEY
```

### Initial Setup
1. Copy `.env.example` to `.env` and configure Google OAuth credentials (see QUICK_SETUP.md)
2. Run `python setup_database.py` to initialize database schema
3. Upload staff CSV via `/admin` page (columns: Code, Last Name, First Name, Email)
4. Use staff codes: VP (admin), DK (teacher), MU (booking staff)

### Testing Authentication
- Visit `/login` to test Google OAuth flow
- Test role access by logging in with different staff emails
- Check role badge appears in navbar after login

### Building/Testing
- **Syntax check**: `python -m py_compile app.py auth.py`
- **No automated tests**: Manual testing via browser required
- **No build step**: Pure Python/Flask, runs directly

## Coding Conventions & Patterns

### Route Protection
```python
@app.route('/recipes')
@require_role('VP', 'DK', 'MU')  # Multiple roles allowed
def recipes_page():
    # Protected route, accessible to specified roles
    pass

@app.route('/recbk')
def recbk():
    # Public route, no decorator needed
    pass
```

### Database Access Pattern
```python
with sqlite3.connect(DATABASE) as conn:
    conn.row_factory = sqlite3.Row  # Enable column access by name
    c = conn.cursor()
    c.execute('SELECT id, name FROM recipes WHERE id = ?', (recipe_id,))
    row = c.fetchone()
    recipe = dict(row)  # Convert to dict for template
```

### JSON Field Handling
```python
# Storing
c.execute('INSERT INTO recipes (name, ingredients) VALUES (?, ?)',
          (name, json.dumps(ingredients_list)))

# Loading
ingredients = json.loads(row['ingredients'] or '[]')
```

### Template Data Preparation
- Always convert `sqlite3.Row` to `dict()` before passing to template
- Parse JSON fields before template rendering
- Use `try/except` blocks when loading JSON (default to empty list/dict on error)

### Flash Messages
```python
flash('Message text', 'success')  # success, error, warning, info
return redirect(url_for('route_name'))
```

## Security Patterns

### OAuth Configuration
- Environment variables: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REDIRECT_URI`
- Dev mode: `OAUTHLIB_INSECURE_TRANSPORT=1` (only when `FLASK_ENV=development`)
- Prod mode: Must use HTTPS, remove insecure transport flag

### Session Management
- User data stored in `session['user']` dict with keys: `google_id`, `email`, `name`, `staff_code`, `role`
- Flask-Login manages authentication state via `current_user`
- Logout clears both session and Flask-Login state

### Permission Checks
- Server-side only via decorators (`@require_role`, `@require_login`)
- No client-side permission enforcement
- Role permissions can be customized in `role_permissions` table

## File Structure
- `app.py` - Main Flask app with all routes (2000+ lines, monolithic)
- `auth.py` - User model and authorization decorators
- `recipe_parser.py` - PDF recipe extraction logic
- `setup_database.py` - Database schema initialization
- `templates/` - Jinja2 templates for all pages
- `static/` - CSS, JS, images, uploaded recipe photos
- `.env` - Secrets and config (gitignored, use `.env.example` as template)

## Common Tasks

### Adding a New Protected Route
1. Define route function in `app.py`
2. Add `@require_role('VP', 'DK')` decorator with allowed roles
3. Add route to `role_permissions` table or use `setup_database.py` defaults
4. Update navbar in relevant templates

### Adding a Recipe via Code
```python
c.execute('INSERT INTO recipes (name, ingredients, instructions, serving_size, equipment) VALUES (?, ?, ?, ?, ?)',
          (name, json.dumps(ingredients_list), instructions_text, serving_int, json.dumps(equipment_list)))
```

### Modifying Permissions
- Update `role_permissions` table in database
- Or modify `ROLE_PERMISSIONS` dict in `auth.py` (legacy fallback)
- Restart app for changes to take effect

## Important Notes
- **Single database file**: All data in `recipes.db` - back up regularly
- **No migrations**: Schema changes require manual ALTER TABLE or rebuild
- **Monolithic structure**: All routes in `app.py` - consider refactoring for large changes
- **Session-based auth**: No JWT, uses Flask session cookies
- **Manual testing only**: No pytest/unittest infrastructure
