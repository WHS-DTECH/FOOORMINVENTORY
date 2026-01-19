# Food Room Inventory SiteMap & Admin Navigation

## Main Navigation Bar (Sitemap)
The main navigation bar is defined in `navigation_main/templates/navigation_main/nav.html` and included in `base.html`. All templates that extend `base.html` inherit this navigation bar.

### Main Navigation Links
- Food Room inventory (`url_for('index')`)
- Recipe Book (`url_for('recbk')`)
- Class Ingredients (`url_for('class_ingredients')`)
- Book the Shopping (`url_for('shoplist.book_the_shopping')`)
- Admin (dropdown for admins, single link for others)
  - Admin Dashboard
  - Recipe Book Setup
  - Manage Role Permissions
  - Manage User Roles
  - Recipe Suggestions
- User info and Logout (if authenticated)
- Login (if not authenticated)

### Which Files Use the Main Navigation
- All templates that extend `base.html` have the main navigation bar.
- Example templates: `welcome.html`, `recbk.html`, `class_ingred.html`, `edit_instructions.html`, `recipe_details.html`, `review_recipe_url.html`, `search_results.html`, `test_recipe_urls.html`, `upload_recipe.html`, `url_upload.html`, etc.
- Any template not extending `base.html` or not including `navigation_main/nav.html` directly will not have the main navigation.
- `recipes.html` and `shoplist_new.html` were previously exceptions, but have now been updated for consistency.

## Admin Dropdown (for Admins)

### Primary File Links and Endpoints
- **Admin Dashboard**  
  - Endpoint: `url_for('admin')`  
  - File: `admin_task/admin_routes.py` (function: `admin`)  
  - Template: `admin_task/templates/admin_task/admin.html`

- **Recipe Book Setup**  
  - Endpoint: `url_for('admin_recipe_book_setup')`  
  - File: `admin_task/admin_routes.py` (handled after uploading class CSV, renders `recipe_book_setup.html`)  
  - Template: `admin_task/templates/admin_task/recipe_book_setup.html`

- **Manage Role Permissions**  
  - Endpoint: `url_for('admin_permissions')`  
  - Template: `admin_task/templates/admin_task/admin_permissions.html`

- **Manage User Roles**  
  - Endpoint: `url_for('admin_user_roles')`  
  - Template: `admin_task/templates/admin_task/admin_user_roles.html`

- **Recipe Suggestions**  
  - Endpoint: `url_for('recipe_suggestions')`  
  - Template: `admin_task/templates/admin_task/admin_recipe_suggestions.html`

---

This file documents the navigation structure and admin links for the Food Room Inventory system. Update as needed when navigation or admin features change.
