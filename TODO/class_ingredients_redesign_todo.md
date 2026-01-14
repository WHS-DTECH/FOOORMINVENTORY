# TODO: Class Ingredients Page Redesign (Professional UI)

## 1. Modern Card Layout
- Group related sections (Staff/Class selection, Recipe selection, Ingredients, Bookings) into visually distinct cards or panels with subtle shadows and rounded corners.
- Use a two-column layout on desktop:
  - Left column: Staff/Class/Recipe selection and ingredient calculation
  - Right column: Scheduled Bookings

## 2. Visual Hierarchy & Spacing
- Add more white space between sections and form elements.
- Use larger, bold section headings and subtle dividers.
- Use consistent padding inside cards and around buttons.

## 3. Typography & Colors
- Use a modern sans-serif font (e.g., Roboto, Open Sans).
- Use a primary color for buttons and highlights (e.g., blue or green).
- Use muted background colors for cards (e.g., #f9f9f9) and a slightly darker background for the page.

## 4. Form Improvements
- Use dropdowns with search for Staff/Class/Recipe (e.g., Select2 or native HTML5 datalist).
- Place the "Calculate" and "Save booking" buttons side-by-side, styled as primary and secondary actions.
- Add tooltips or helper text for fields like "Desired Servings".

## 5. Scheduled Bookings Table
- Use a striped table with hover effects.
- Add icons for actions (e.g., a trash can for Delete).
- Make the table responsive for mobile devices.

## 6. Responsive Design
- On mobile, stack cards vertically and make buttons full-width.
- Use media queries to adjust padding, font size, and layout.

## 7. CSS/Framework Suggestions
- Use a CSS framework like Bootstrap or Bulma for quick, professional results.
- Or, add your own CSS for:
  - .card { background: #f9f9f9; border-radius: 8px; box-shadow: 0 2px 8px #0001; padding: 1.5em; margin-bottom: 1.5em; }
  - .btn-primary { background: #007bff; color: #fff; border-radius: 4px; }
  - .table-striped tr:nth-child(even) { background: #f2f2f2; }

## 8. Implementation Plan
- Install and configure a modern CSS framework (Bootstrap or Bulma) via npm, CDN, or static files.
- Refactor the HTML structure of class_ingred.html to use cards, columns, and improved form controls.
- Update static/styles.css to override or extend framework styles as needed.
- Test on desktop and mobile for responsiveness and usability.
- Get user feedback and iterate as needed.
