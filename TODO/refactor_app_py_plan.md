# Refactor app.py Migration Plan

## Step-by-Step TODOs

1. Move Utility Functions
   - Create utils.py (or ingredients/utils.py)
   - Move simple_similarity, categorize_ingredient, etc.
   - Update imports in app.py and other files

2. Move Jinja2 Filters
   - Create jinja_filters.py
   - Move datetimeformat, format_nz_week, etc.
   - Register filters in app.py

3. Move Error Handlers
   - Create error_handlers.py
   - Move 404 and 500 error handler functions
   - Register in app.py

4. Move AnonymousUser Class
   - Create auth/anonymous_user.py
   - Move AnonymousUser class
   - Update Flask-Login setup in app.py

5. Move Authentication Routes
   - Create auth/routes.py
   - Move /login, /auth/google, /auth/callback, /logout
   - Register blueprint in app.py

6. Move Recipe Extraction/Review/Flagging Routes
   - Create recipe_book/routes.py or parser/routes.py
   - Move extraction/review/flagging routes
   - Register blueprint in app.py

7. Move API Routes
   - Create api/routes.py
   - Move API endpoints (e.g., /api/update-recipe-tags)
   - Register blueprint in app.py

8. Move Redirects and Miscellaneous Routes
   - Create navigation/routes.py
   - Move redirects/navigation routes
   - Register blueprint in app.py

9. Clean Up app.py
   - Remove all moved logic
   - Ensure only imports, app creation/config, blueprint registration remain

10. Test and Commit
   - Test after each step
   - Commit changes to git with clear messages
