# TODO: Admin Page Professional Redesign

## Visual & Layout Improvements
- [ ] Use consistent card heights and padding for both columns
- [ ] Add more vertical spacing between sections for clarity
- [ ] Align the top of both columns
- [ ] Use larger, bolder section headings
- [ ] Add subtle section dividers or background shading to visually separate areas
- [ ] Use consistent font sizes for labels, buttons, and table headers
- [ ] Add a little more vertical spacing between the “Class & Staff Setup” and “Suggestions List” sections for clarity.
- [ ] Slightly increase the padding inside cards for a more “airy” feel.
- [ ] Make all action buttons (Upload, Clean, Load, etc.) the same height and style for a unified look.
- [ ] Add icons to all major action buttons for quick recognition (e.g., upload, clean, load).
- [ ] Ensure all buttons and form fields have clear labels and ARIA attributes.
- [ ] Add keyboard focus outlines for all interactive elements.
- [ ] Show a toast or alert when uploads/cleans succeed or fail, not just a page reload or flash message.
- [ ] Consider a loading spinner or disabled state on buttons during long actions (like PDF upload or cleaning).
- [ ] Make the “URL” column clickable for all valid links (open in new tab).
- [ ] Add a “Delete” or “Mark as Done” action for suggestions (if appropriate for your workflow).
- [ ] Consider zebra striping or hover highlight for table rows for easier reading.
- [ ] On mobile, stack the two columns vertically and ensure all cards are full-width.
- [ ] Ensure the suggestions table scrolls horizontally on small screens.
- [ ] Add subtle card shadows and slightly round the corners for a softer look.
- [ ] Use a slightly larger font for section headings for easier scanning.

---

# REVISED: Admin Page Redesign Checklist (2026)

## Visual & Layout
- [x] Consistent card heights, padding, and alignment for both columns
- [x] Larger, bolder section headings with icons for quick recognition
- [x] Subtle section dividers or background shading to visually separate areas
- [x] More vertical spacing between sections (especially between Class & Staff Setup and Suggestions List)
- [x] Slightly increased card padding for a more “airy” feel
- [x] Subtle box-shadow and consistent border-radius for all cards and buttons

## Buttons & Forms
- [x] Consistent button colors and sizes for similar actions
- [x] All major action buttons have icons (upload, clean, manage, etc.)
- [x] Full-width buttons on mobile
- [x] File name shown after selection
- [x] All buttons and form fields have clear labels and ARIA attributes
- [x] Keyboard focus outlines for all interactive elements
- [ ] Drag-and-drop support for file uploads (optional/future)
- [ ] Progress indicators or loading spinners for uploads/cleans (optional/future)

## Table & Data Display
- [x] Zebra striping or hover highlight for Suggestions List table rows
- [x] Table header sticky for long lists
- [x] Tooltips or ellipsis for long text in table cells
- [x] “View” link in URL column is a button or icon, opens in new tab
- [x] “Delete” or “Mark as Done” action for suggestions (if appropriate)
- [x] Suggestions table scrolls horizontally on small screens

## Feedback & Validation
- [x] Success/error messages shown near relevant form after upload/action
- [x] Toast or alert for uploads/cleans (not just page reload/flash)
- [x] Modals for confirmation on destructive actions (e.g., Clean Recipe Database)
- [x] Loading spinner or disabled state on buttons during long actions

## Responsiveness & Accessibility
- [x] Two-column layout stacks vertically on mobile, all cards full-width
- [x] Bootstrap grid system for responsiveness
- [x] All buttons and links are keyboard accessible
- [x] Proper label associations for form fields
- [x] Color contrast and font size meet accessibility standards

## General Polish
- [x] Hover effects for buttons and table rows
- [x] Consistent spacing and alignment throughout
- [x] Slightly larger font for section headings

## Optional/Future Features
- [ ] Drag-and-drop support for file uploads (for Staff/Class CSV and PDF uploads)
- [ ] Progress indicators or loading spinners for uploads and database cleaning actions
- [ ] Undo option for destructive actions (e.g., after cleaning or deleting a suggestion)
- [ ] Bulk actions for Suggestions List (e.g., mark multiple as done/delete)
- [ ] Advanced filtering/search for Suggestions List
- [ ] Export Suggestions List to CSV/Excel
- [ ] Inline editing for Suggestions List (edit reason, mark as reviewed, etc.)
- [ ] Admin activity log (track who performed which actions)
- [ ] Customizable roles/permissions UI (drag to reorder, add new roles)
- [ ] Theming options (light/dark mode toggle)
- [ ] Accessibility audit and improvements (using tools like axe or Lighthouse)
- [ ] Automated tests for admin workflows

---

## Notes
- All major redesign goals are complete and deployed.
- Optional/future enhancements are marked as such.
- If any new admin features are added, revisit this checklist for consistency.
