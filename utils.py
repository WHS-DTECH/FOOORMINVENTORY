def simple_similarity(a, b):
    """Return a similarity score between 0 and 1 based on Levenshtein distance (if available) or substring match."""
    try:
        import Levenshtein
        return Levenshtein.ratio(a.lower(), b.lower())
    except ImportError:
        # Fallback: substring match
        a, b = a.lower(), b.lower()
        # Simple substring match score
        if a in b or b in a:
            return 0.7
        return 0.0


def categorize_ingredient(ingredient_name):
    """Categorize ingredient by store section."""
    name_lower = ingredient_name.lower()
    # Produce
    produce = ['apple', 'banana', 'orange', 'lemon', 'lime', 'tomato', 'potato', 'onion', 'garlic', 
               'carrot', 'lettuce', 'spinach', 'cabbage', 'broccoli', 'cauliflower', 'pepper', 'capsicum',
               'cucumber', 'zucchini', 'mushroom', 'avocado', 'celery', 'ginger', 'herbs', 'parsley',
               'cilantro', 'basil', 'mint', 'thyme', 'rosemary', 'kale', 'chard', 'beetroot', 'pumpkin']
    # Dairy
    dairy = ['milk', 'cream', 'butter', 'cheese', 'yogurt', 'yoghurt', 'sour cream', 'feta', 'mozzarella',
             'parmesan', 'cheddar', 'brie', 'cottage cheese', 'ricotta', 'halloumi']
    # Meat & Seafood
    meat = ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'bacon', 'sausage', 'mince', 'steak',
            'fish', 'salmon', 'tuna', 'prawns', 'shrimp', 'mussels', 'seafood']
    # Pantry/Dry Goods
    pantry = ['flour', 'sugar', 'rice', 'pasta', 'bread', 'cereal', 'oats', 'quinoa', 'couscous',
              'lentils', 'beans', 'chickpeas', 'oil', 'vinegar', 'sauce', 'stock', 'broth',
              'honey', 'jam', 'peanut butter', 'nuts', 'almonds', 'cashews', 'seeds', 'spice',
              'salt', 'pepper', 'cumin', 'paprika', 'cinnamon', 'vanilla', 'cocoa', 'chocolate',
              'baking powder', 'baking soda', 'yeast', 'cornstarch', 'cornflour']
    # Frozen
    frozen = ['frozen', 'ice cream', 'peas', 'corn', 'berries mixed']
    # Beverages
    beverages = ['juice', 'soda', 'water', 'tea', 'coffee', 'wine', 'beer']
    # Check categories
    for item in produce:
        if item in name_lower:
            return 'Produce'
    for item in dairy:
        if item in name_lower:
            return 'Dairy'
    for item in meat:
        if item in name_lower:
            return 'Meat & Seafood'
    for item in pantry:
        if item in name_lower:
            return 'Pantry'
    for item in frozen:
        if item in name_lower:
            return 'Frozen'
    for item in beverages:
        if item in name_lower:
            return 'Beverages'
    return 'Other'
