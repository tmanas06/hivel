# hivel

company code round

for menu_api.py

{
    "combos": [
        {
            "drink": {
                "calories": 100,
                "name": "Masala Chaas",
                "taste_profile": "spicy"
            },
            "main": {
                "calories": 450,
                "name": "Paneer Butter Masala",
                "popularity": 0.9,
                "taste_profile": "spicy"
            },
            "remark": "A satisfying combination of Paneer Butter Masala, Garlic Naan, and Masala Chaas (Total: 750 kcal).",
            "side": {
                "calories": 200,
                "name": "Garlic Naan",
                "taste_profile": "savory"
            }
        },
        {
            "drink": {
                "calories": 220,
                "name": "Sweet Lassi",
                "taste_profile": "sweet"
            },
            "main": {
                "calories": 600,
                "name": "Chicken Biryani",
                "popularity": 0.95,
                "taste_profile": "spicy"
            },
            "remark": "Try our Chicken Biryani with Mixed Veg Salad and Sweet Lassi - a customer favorite!",
            "side": {
                "calories": 150,
                "name": "Mixed Veg Salad",
                "taste_profile": "sweet"
            }
        },
        {
            "drink": {
                "calories": 90,
                "name": "Lemon Soda",
                "taste_profile": "savory"
            },
            "main": {
                "calories": 400,
                "name": "Vegetable Pulao",
                "popularity": 0.7,
                "taste_profile": "savory"
            },
            "remark": "Enjoy our Vegetable Pulao (popularity: 70%) with French Fries, complemented by Lemon Soda.",
            "side": {
                "calories": 350,
                "name": "French Fries",
                "taste_profile": "savory"
            }
        }
    ],
    "date": "2025-07-24",
    "status": "success"
}


for upmenu_api.py

🔸 Taste Profiles
If all items share the same taste (e.g., all spicy) → "unified spicy profile"

If flavors are different but complement well → "complementary flavor combination"

🔸 Calories
1000 → "hearty meal"

700 → "satisfying portion"

≤700 → "light option"

🔸 Special Tags
If “spicy” or “sweet” is present → "spicy kick", "sweet notes"

If it's a very popular main dish → "popular choice"

The combo is constructed based on fair usage,
but the reasoning is generated based on taste + calorie profile + popularity.