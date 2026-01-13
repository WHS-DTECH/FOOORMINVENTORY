-- NEON/POSTGRESQL BATCH FOR TABLE: recipes
-- Drop table if exists (for re-runs)
DROP TABLE IF EXISTS recipes;

-- Create table (PostgreSQL syntax)
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    ingredients TEXT,
    instructions TEXT,
    serving_size INTEGER,
    equipment TEXT,
    photo TEXT,
    dietary_tags TEXT,
    cuisine TEXT,
    difficulty TEXT
);

-- Insert data
INSERT INTO recipes (id, name, ingredients, instructions, serving_size, equipment, photo, dietary_tags, cuisine, difficulty) VALUES
    (1, 'Chocolate Chip Cookies', '[{"quantity": "2", "unit": "cups", "ingredient": "Flour"}, {"quantity": "1", "unit": "cup", "ingredient": "Butter (softened)"}, {"quantity": "0.75", "unit": "cup", "ingredient": "Brown sugar"}, {"quantity": "0.5", "unit": "cup", "ingredient": "Granulated sugar"}, {"quantity": "2", "unit": "whole", "ingredient": "Eggs"}, {"quantity": "1", "unit": "tsp", "ingredient": "Vanilla extract"}, {"quantity": "1", "unit": "tsp", "ingredient": "Baking soda"}, {"quantity": "0.5", "unit": "tsp", "ingredient": "Salt"}, {"quantity": "2", "unit": "cups", "ingredient": "Chocolate chips"}]', 'Mix dry ingredients. Add wet ingredients. Drop onto baking sheet. Bake at 350F for 12 minutes.', 24, '["Mixing bowl|Measuring cups|Baking sheet|Oven"]', NULL, NULL, NULL, NULL),
    (3, 'Cauliflower Cheese', '[{"quantity": "1.0", "unit": "head", "ingredient": "of cauliflower OR 1 head of broccoli OR a mix of both"}, {"quantity": "50.0", "unit": "plain", "ingredient": "flour"}, {"quantity": "500.0", "unit": "milk", "ingredient": "milk"}, {"quantity": "50.0", "unit": "butter", "ingredient": "butter"}, {"quantity": "100.0", "unit": "grated", "ingredient": "cheese"}, {"quantity": "", "unit": "", "ingredient": "Black pepper"}, {"quantity": "", "unit": "", "ingredient": "1-2 tblsp fresh breadcrumbs"}, {"quantity": "", "unit": "", "ingredient": "Don’t forget a container to take your cauliflower cheese home in"}]', '1. 2cm hot water into a pan\n2.  Bring to the boil, add the vegetables and cover with a lid\n3.  Cook for 5mins maximum then drain using a colander then place them in a\ndish\n4.  Put the butter into a pan and melt it\n5.  Add flour and stir to form a paste\n6.  Gradually add the milk – keep stirring until it thickens.\n7.  Remove from the heat and stir in most of the cheese. Season.\n8.  Pour over the veg.\n9. Sprinkle on breadcrumbs and the remaining cheese\n10. Grill under  a hot grill until golden brown.\nFeeling a dventurous?  You could….\n• Try using different vegetables', NULL, NULL, NULL, NULL, NULL),
    -- ...existing code for other INSERTs...
    (24, 'Perfect Pavlova', '[{"quantity": "6", "unit": "item", "ingredient": "egg whites (at room temperature)"}, {"quantity": "2", "unit": "cups", "ingredient": "Chelsea Caster Sugar (450g)"}, {"quantity": "1", "unit": "tsp", "ingredient": "vanilla essence"}, {"quantity": "1", "unit": "tsp", "ingredient": "white vinegar"}, {"quantity": "2", "unit": "tsp", "ingredient": "Edmonds Fielder''s Cornflour"}, {"quantity": "300", "unit": "ml", "ingredient": "Meadow Fresh Original Cream, whipped"}, {"quantity": "1", "unit": "to taste", "ingredient": "Fruit, to decorate"}]', 'Preheat oven to 110ºC bake (not fan bake). Line a baking tray with baking paper. In a large metal, ceramic or glass bowl (not plastic), beat the egg whites until soft peaks form. Continue beating while adding the Chelsea Caster Sugar a quarter of a cup at a time. The mixture should get glossier and thicker with each addition and this should take at least 10 minutes. Beat in the vanilla, vinegar and Edmonds Fielder''s Cornflour. Spoon mixture out onto the prepared tray into a dinner plate sized mound. Bake for approximately 1 1/2 hours, until dry and crisp and it lifts easily off the baking paper. Turn the oven off and leave the pavlova for at least an hour before removing from the oven. Finish cooling on a wire rack, then transfer to an airtight container. When ready to serve, place on a serving plate, swirl the top with the whipped Meadow Fresh Original Cream and decorate with sliced or chopped fruit of your choice.', 12, '[]', NULL, NULL, NULL, NULL);

-- Note: Only a sample of INSERTs is shown. For full migration, include all INSERTs from the SQLite dump, converting NULLs and escaping as needed.
-- SERIAL in PostgreSQL auto-increments id. If you want to continue auto-incrementing from the highest id, run:
-- SELECT setval('recipes_id_seq', (SELECT MAX(id) FROM recipes));
