import random
import pandas as pd
from flask import Flask, jsonify, Response
from datetime import datetime
from collections import OrderedDict

app = Flask(__name__)

class MenuGenerator:
    def __init__(self, csv_path):
        # Reading CSV
        self.df = pd.read_csv(csv_path)
        
        # Convert category to lowercase
        self.df['category'] = self.df['category'].str.lower()
        
        # Get items by category
        self.mains = self.df[self.df['category'].str.lower() == 'main'].to_dict('records')
        self.sides = self.df[self.df['category'].str.lower() == 'side'].to_dict('records')
        self.drinks = self.df[self.df['category'].str.lower() == 'drink'].to_dict('records')
        
        self.used_combinations = set()
        self.usage_count = {}
        
        # Initialize usage counts for all items
        for item in self.mains + self.sides + self.drinks:
            self.usage_count[item['item_name']] = 0

    def generate_combos(self):
        # Reset used combinations if all items have been used at least once
        if all(count > 0 for count in self.usage_count.values()):
            self.usage_count = {k: 0 for k in self.usage_count}
            self.used_combinations = set()

        combos = []
        
        # We need to generate 3 combos
        for _ in range(3):
            while True:
                # Get least used items first
                main = min(self.mains, key=lambda x: self.usage_count[x['item_name']])
                side = min(self.sides, key=lambda x: self.usage_count[x['item_name']])
                drink = min(self.drinks, key=lambda x: self.usage_count[x['item_name']])
                
                combo_key = (main['item_name'], side['item_name'], drink['item_name'])
                
                # If this exact combo hasn't been used before, use it
                if combo_key not in self.used_combinations:
                    self.used_combinations.add(combo_key)
                    self.usage_count[main['item_name']] += 1
                    self.usage_count[side['item_name']] += 1
                    self.usage_count[drink['item_name']] += 1
                    
                    # Generate reasoning for the combination
                    reasoning = self._generate_reasoning(main, side, drink)
                    
                    # Create combo with reasoning
                    combo = {
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
                    combos.append(combo)
                    break
                
                # If we're stuck in a loop, clear used combinations and try again
                if len(self.used_combinations) >= (len(self.mains) * len(self.sides) * len(self.drinks)):
                    self.used_combinations = set()
        
        return combos
    
    def _generate_reasoning(self, main, side, drink):
        calorie_total = int(float(main['calories']) + float(side['calories']) + float(drink['calories']))
        popularity = float(main['popularity_score'])
        taste_profiles = {main['taste_profile'], side['taste_profile'], drink['taste_profile']}
        today = datetime.now().strftime('%A').lower()

        # Build reasoning components
        reasons = []
        
        # Taste profile analysis
        if len(taste_profiles) == 1:
            reasons.append(f"unified {main['taste_profile']} profile")
        else:
            profile_str = ", ".join(taste_profiles)
            reasons.append(f"complementary {profile_str} flavors")
        
        # Popularity
        if popularity >= 0.9:
            reasons.append("popular choice")
        
        # Taste-based features
        if "spicy" in taste_profiles:
            reasons.append("spicy kick")
        elif "sweet" in taste_profiles:
            reasons.append("sweet notes")
        
        # Calorie range
        if calorie_total > 1000:
            reasons.append("hearty meal")
        elif calorie_total > 700:
            reasons.append("satisfying portion")
        else:
            reasons.append("light option")
        
        # Ensure we have at least 3 reasons
        if len(reasons) < 3:
            if calorie_total > 1000:
                reasons.append("high-energy meal")
            elif calorie_total < 600:
                reasons.append("low-calorie choice")
            
            if len(taste_profiles) > 1:
                reasons.append("great flavor combination")
        
        # Join the first 3 reasons for concise output
        return ", ".join(reasons[:3])

# Initialize the menu generator with the provided CSV file
menu_generator = MenuGenerator('AI_Menu_Recommender_Items.csv')

@app.route('/api/menu', methods=['GET'])
def get_menu():
    try:
        if not menu_generator.mains or not menu_generator.sides or not menu_generator.drinks:
            return jsonify({
                'status': 'error',
                'message': 'Insufficient menu items. Please ensure there is at least one item in each category (main, side, drink).',
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
                'message': 'Failed to generate menu combinations. Please check your menu items.',
                'available_items': {
                    'mains': [item['item_name'] for item in menu_generator.mains],
                    'sides': [item['item_name'] for item in menu_generator.sides],
                    'drinks': [item['item_name'] for item in menu_generator.drinks]
                }
            }), 500
            
        # Format response as flat list with combo_id
        formatted_combos = []
        for idx, combo in enumerate(combos, 1):
            main_name = combo['main']['name']
            side_name = combo['side']['name']
            drink_name = combo['drink']['name']
            total_calories = int(combo['main']['calories'] + combo['side']['calories'] + combo['drink']['calories'])
            
            # Get reasoning from the combo (already generated in generate_combos)
            reasoning = combo.get('reasoning', 'No reasoning provided')
            
            formatted_combos.append({
                'combo_id': idx,
                'main': main_name,
                'side': side_name,
                'drink': drink_name,
                'total_calories': total_calories,
                'reasoning': reasoning
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
