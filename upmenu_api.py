import random
import pandas as pd
from flask import Flask, jsonify
from datetime import datetime

app = Flask(__name__)

class MenuGenerator:
    def __init__(self, csv_path):
        # Reading CSV
        self.df = pd.read_csv(csv_path)
        
        # Convert category to lowercase
        self.df['category'] = self.df['category'].str.lower()
        
        # Get items by category
        self.mains = self.df[self.df['category'] == 'main'].to_dict('records')
        self.sides = self.df[self.df['category'] == 'side'].to_dict('records')
        self.drinks = self.df[self.df['category'] == 'drink'].to_dict('records')
        
        self.used_combinations = set()
        self.usage_count = {}
        
        # Initialize usage counts for all items
        for item in self.mains + self.sides + self.drinks:
            self.usage_count[item['item_name']] = 0

    def total_unique_combos(self):
        return len(self.mains) * len(self.sides) * len(self.drinks)

    def generate_combos(self):
        # Reset used combos if all possible combos are exhausted
        if len(self.used_combinations) >= self.total_unique_combos():
            self.used_combinations.clear()
            self.usage_count = {k: 0 for k in self.usage_count}

        random.shuffle(self.mains)
        random.shuffle(self.sides)
        random.shuffle(self.drinks)

        used_mains = set()
        used_sides = set()
        used_drinks = set()

        # Find base combo to determine target calories
        target_calories = None
        base_combo = None
        for main in self.mains:
            for side in self.sides:
                for drink in self.drinks:
                    combo_key = (main['item_name'], side['item_name'], drink['item_name'])
                    if combo_key not in self.used_combinations:
                        target_calories = int(main['calories']) + int(side['calories']) + int(drink['calories'])
                        base_combo = {'main': main, 'side': side, 'drink': drink}
                        break
                if target_calories is not None:
                    break
            if target_calories is not None:
                break

        if target_calories is None:
            # No combos left
            return []

        combos = []

        # Add base combo and mark items used
        main, side, drink = base_combo['main'], base_combo['side'], base_combo['drink']
        combo_key = (main['item_name'], side['item_name'], drink['item_name'])
        self.used_combinations.add(combo_key)
        self.usage_count[main['item_name']] += 1
        self.usage_count[side['item_name']] += 1
        self.usage_count[drink['item_name']] += 1

        used_mains.add(main['item_name'])
        used_sides.add(side['item_name'])
        used_drinks.add(drink['item_name'])

        combos.append(self._format_combo(main, side, drink))

        combos_found = 1

        # Find 2 more combos with no repeating main, side, or drink and calories within ±10
        for main in self.mains:
            if combos_found >= 3:
                break
            if main['item_name'] in used_mains:
                continue
            for side in self.sides:
                if combos_found >= 3:
                    break
                if side['item_name'] in used_sides:
                    continue
                for drink in self.drinks:
                    if combos_found >= 3:
                        break
                    if drink['item_name'] in used_drinks:
                        continue
                    combo_key = (main['item_name'], side['item_name'], drink['item_name'])
                    combo_calories = int(main['calories']) + int(side['calories']) + int(drink['calories'])
                    if combo_key not in self.used_combinations and abs(combo_calories - target_calories) <= 10:
                        self.used_combinations.add(combo_key)
                        self.usage_count[main['item_name']] += 1
                        self.usage_count[side['item_name']] += 1
                        self.usage_count[drink['item_name']] += 1

                        used_mains.add(main['item_name'])
                        used_sides.add(side['item_name'])
                        used_drinks.add(drink['item_name'])

                        combos.append(self._format_combo(main, side, drink))
                        combos_found += 1

        return combos

    def _format_combo(self, main, side, drink):
        reasoning = self._generate_reasoning(main, side, drink)
        return {
            'main': {
                'name': main['item_name'],
                'calories': int(main['calories']),
                'taste_profile': main['taste_profile'],
                'popularity': float(main['popularity_score'])
            },
            'side': {
                'name': side['item_name'],
                'calories': int(side['calories']),
                'taste_profile': side['taste_profile']
            },
            'drink': {
                'name': drink['item_name'],
                'calories': int(drink['calories']),
                'taste_profile': drink['taste_profile']
            },
            'reasoning': reasoning
        }

    def _generate_reasoning(self, main, side, drink):
        calorie_total = int(float(main['calories']) + float(side['calories']) + float(drink['calories']))
        popularity = float(main['popularity_score'])
        taste_profiles = {main['taste_profile'], side['taste_profile'], drink['taste_profile']}

        reasons = []

        if len(taste_profiles) == 1:
            reasons.append(f"unified {main['taste_profile']} profile")
        else:
            profile_str = ", ".join(taste_profiles)
            reasons.append(f"complementary {profile_str} flavors")

        if popularity >= 0.9:
            reasons.append("popular choice")

        if "spicy" in taste_profiles:
            reasons.append("spicy kick")
        elif "sweet" in taste_profiles:
            reasons.append("sweet notes")

        if calorie_total > 1000:
            reasons.append("hearty meal")
        elif calorie_total > 700:
            reasons.append("satisfying portion")
        else:
            reasons.append("light option")

        # Ensure at least 3 reasons
        if len(reasons) < 3:
            if calorie_total > 1000:
                reasons.append("high-energy meal")
            elif calorie_total < 600:
                reasons.append("low-calorie choice")
            if len(taste_profiles) > 1:
                reasons.append("great flavor combination")

        return ", ".join(reasons[:3])

menu_generator = MenuGenerator('AI_Menu_Recommender_Items.csv')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    try:
        if not menu_generator.mains or not menu_generator.sides or not menu_generator.drinks:
            return jsonify({
                'status': 'error',
                'message': 'Insufficient menu items. Please ensure at least one item in each category (main, side, drink).',
                'available_items': {
                    'mains': [item['item_name'] for item in menu_generator.mains],
                    'sides': [item['item_name'] for item in menu_generator.sides],
                    'drinks': [item['item_name'] for item in menu_generator.drinks]
                }
            }), 400

        combos = menu_generator.generate_combos()

        if not combos:
            return jsonify({
                'status': 'error',
                'message': 'All unique menu combinations have been generated. Please reset or add more items.',
                'available_items': {
                    'mains': [item['item_name'] for item in menu_generator.mains],
                    'sides': [item['item_name'] for item in menu_generator.sides],
                    'drinks': [item['item_name'] for item in menu_generator.drinks]
                }
            }), 200

        formatted_combos = []
        for idx, combo in enumerate(combos, 1):
            total_calories = combo['main']['calories'] + combo['side']['calories'] + combo['drink']['calories']
            formatted_combos.append({
                'combo_id': idx,
                'main': combo['main']['name'],
                'side': combo['side']['name'],
                'drink': combo['drink']['name'],
                'total_calories': total_calories,
                'reasoning': combo['reasoning']
            })

        return jsonify(formatted_combos)

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'error': str(e),
            'details': error_details if app.debug else None
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)