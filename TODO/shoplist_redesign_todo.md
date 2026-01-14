# Shopping List Page Redesign TODO

## Issues & Suggestions (2026-01-15)

1. **Selected Bookings Buttons Visibility in Month View**
   - Hide “Select All”, “Clear”, and “Auto Generate” buttons (and Selected Bookings panel) in Month View. Only show in Week/Period View.

2. **Visual Hierarchy & Spacing**
   - Add more vertical spacing between major sections.
   - Use card or panel backgrounds for Selected Bookings and Shopping List sections.

3. **Button Styling & Placement**
   - Make “Generate Shopping List” and “Print Shopping List Only” more visually prominent.
   - Group related actions together in a card or panel.

4. **Mobile Responsiveness**
   - Ensure grid/table scrolls horizontally on small screens.
   - Stack controls vertically on mobile.

5. **Accessibility**
   - Add ARIA labels to all interactive elements.
   - Ensure all buttons and controls are keyboard accessible.

6. **Calendar Improvements**
   - In Month View, add tooltip or modal on click for each booking to show details.
   - Consider a legend for teacher colors in Month View.

7. **Shopping List Clarity**
   - Use headings and dividers to separate each teacher’s shopping list.
   - Consider collapsible panels for each teacher.

8. **Performance**
   - For large numbers of bookings, consider paginating or lazy-loading the grid/calendar.

9. **Feedback States**
   - Show a loading spinner or feedback message when generating the shopping list.

10. **Consistency**
   - Ensure button styles, card backgrounds, and font sizes are consistent across both views.

## Optional Enhancements
- Add export options (CSV, PDF) for shopping lists.
- Allow multi-select and bulk actions for bookings.
- Add a summary panel for total quantities needed.
- Enable drag-and-drop for booking selection.

# MASTER TODO: Redesign & Bugfix Checklist

- [ ] 1. Run /admin/fix_public_roles route as VP
  - Visit /admin/fix_public_roles while logged in as VP to ensure all users have 'public' in user_roles table.
- [ ] 2. Review Admin user roles UI
  - Ensure admin user roles page displays all users, including those with only 'public' role.
- [ ] 3. Complete Shopping List redesign tasks
  - Work through all items in this file and confirm each is done.
- [ ] 4. Polish Recipe Book, Class Ingredients, Admin, and mobile/accessibility improvements
  - Review and finalize all redesigns for these pages, including mobile and accessibility features.
- [ ] 5. Confirm backend/template errors are resolved in production
  - Test all major pages (including landing page) to ensure no errors remain.
- [ ] 6. Ensure database state matches UI logic for roles/permissions
  - Verify that user_roles and permissions in the database match what is shown in the UI.
- [ ] 7. Address new issues from user testing
  - Triage and fix any new bugs or feedback from ongoing user testing.
