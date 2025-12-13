#!/usr/bin/env python3
"""Test if parser can extract Beef Nachos and Forfar Bridies."""

import sys
sys.path.insert(0, '/home/WHSDTECH/FOOORMINVENTORY')

from recipe_parser import parse_recipes_from_text
import PyPDF2

# Test with Year 8 PDF - Beef Nachos on page 45
print("Testing Year 8 PDF for Beef Nachos...")
with open('/home/WHSDTECH/FOOORMINVENTORY/RecipesPDF/Year 8 Recipe Book.pdf', 'rb') as f:
    pdf = PyPDF2.PdfReader(f)
    page_45 = pdf.pages[44]  # 0-indexed
    text = page_45.extract_text()
    
    print("\n=== PAGE 45 TEXT ===")
    print(text[:1000])
    
    print("\n=== PARSING RESULTS ===")
    recipes = parse_recipes_from_text(text)
    print(f"Found {len(recipes)} recipe(s):")
    for r in recipes:
        print(f"  - {r['name']}")

print("\n" + "="*80)
print("\nTesting Year 7 PDF for Forfar Bridies...")
with open('/home/WHSDTECH/FOOORMINVENTORY/RecipesPDF/Year 7 Recipe Book.pdf', 'rb') as f:
    pdf = PyPDF2.PdfReader(f)
    page_49 = pdf.pages[48]  # 0-indexed
    text = page_49.extract_text()
    
    print("\n=== PAGE 49 TEXT ===")
    print(text[:1000])
    
    print("\n=== PARSING RESULTS ===")
    recipes = parse_recipes_from_text(text)
    print(f"Found {len(recipes)} recipe(s):")
    for r in recipes:
        print(f"  - {r['name']}")
