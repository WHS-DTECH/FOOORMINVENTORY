# Parser Testing System TODO

## 1. Test Suite Setup
- [ ] Create a list/database of diverse recipe URLs for testing (various sites, formats, edge cases)
- [ ] Add a way to flag and add new problematic URLs to the test suite

## 2. Automated Testing
- [ ] Build a script or Flask route to run all test URLs through the parser
- [ ] Log which parser steps are used and the extracted instructions for each recipe
- [ ] Save results for review and regression tracking

## 3. Coverage Dashboard
- [ ] Create a UI/dashboard to visualize which steps succeeded/failed for each recipe
- [ ] Highlight recipes with poor extraction or missing steps

## 4. Parser Modularity
- [ ] Refactor parser so each extraction method is a separate function
- [ ] Ensure step logging is accurate and only fallback if previous steps fail

## 5. Incremental Improvements
- [ ] When updating the parser, add new logic as new steps (do not remove old steps unless broken)
- [ ] After each change, re-run the full test suite and check for regressions
- [ ] Document what each step is designed to handle

## 6. Version Control & Changelog
- [ ] Commit each parser change with notes about which recipes/issues it addresses
- [ ] Maintain a changelog of improvements and regressions

## 7. Team/User Feedback
- [ ] Allow users/team to submit URLs that fail or are poorly parsed
- [ ] Add submitted URLs to the test suite for future parser improvements

---
This TODO list will help guide the development of a robust, maintainable, and transparent parser testing system for recipe extraction.