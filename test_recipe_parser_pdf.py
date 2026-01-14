import unittest
from recipe_parser_pdf import parse_recipes_from_text

class TestRecipeParserPDF(unittest.TestCase):
    def test_missing_sections(self):
        text = """
        Recipe: Simple Toast
        Ingredients
        2 slices bread
        1 tbsp butter
        Method
        1. Toast bread
        2. Spread butter
        """
        result = parse_recipes_from_text(text)
        self.assertTrue(result)
        recipes = result['recipes'] if isinstance(result, dict) else result
        self.assertEqual(len(recipes), 1)
        self.assertEqual(recipes[0]['name'], 'Simple Toast')
        self.assertIn('bread', recipes[0]['ingredients'][0]['ingredient'])

    def test_unusual_formatting(self):
        text = """
        RECIPE: ODD FORMAT
        INGREDIENTS
        1 cup milk
        2 eggs
        EQUIPMENT
        Bowl; Whisk
        METHOD
        - Beat eggs
        - Add milk
        """
        result = parse_recipes_from_text(text)
        recipes = result['recipes'] if isinstance(result, dict) else result
        self.assertEqual(len(recipes), 1)
        self.assertIn('milk', recipes[0]['ingredients'][0]['ingredient'])
        self.assertIn('Bowl', recipes[0]['equipment'][0])
        self.assertIn('Beat eggs', recipes[0]['method'])

    def test_multi_recipe_pdf(self):
        text = """
        Recipe: First
        Ingredients
        1 apple
        Method
        1. Eat apple
        Recipe: Second
        Ingredients
        1 banana
        Method
        1. Eat banana
        """
        result = parse_recipes_from_text(text)
        recipes = result['recipes'] if isinstance(result, dict) else result
        self.assertEqual(len(recipes), 2)
        self.assertEqual(recipes[0]['name'], 'First')
        self.assertEqual(recipes[1]['name'], 'Second')

    def test_edge_case_notes_tips(self):
        text = """
        Recipe: With Notes
        Ingredients
        1 egg
        Method
        1. Crack egg
        Notes: Use fresh eggs
        Tips: Add salt
        """
        result = parse_recipes_from_text(text)
        recipes = result['recipes'] if isinstance(result, dict) else result
        self.assertEqual(recipes[0]['notes'][0], 'Notes: Use fresh eggs')
        self.assertEqual(recipes[0]['tips'][0], 'Tips: Add salt')

if __name__ == '__main__':
    unittest.main()
