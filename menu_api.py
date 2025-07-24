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
                    
                    # Generate a remark based on the combination
                    remark = self._generate_remark(main, side, drink)
                    
                    combos.append({
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
                        'remark': remark
                    })
                    break
                
                # If we're stuck in a loop, clear used combinations and try again
                if len(self.used_combinations) >= (len(self.mains) * len(self.sides) * len(self.drinks)):
                    self.used_combinations = set()
        
        return combos
    
    def _generate_remark(self, main, side, drink):
        # Generate a remark based on the combination's attributes
        calorie_total = float(main['calories']) + float(side['calories']) + float(drink['calories'])
        
        # Determine meal type based on calories
        if calorie_total > 1000:
            meal_type = "hearty"
        elif calorie_total > 700:
            meal_type = "satisfying"
        else:
            meal_type = "light"
            
        # Taste profile synergy
        taste_synergy = ""
        if main['taste_profile'] == side['taste_profile'] == drink['taste_profile']:
            taste_synergy = f" with a consistent {main['taste_profile']} profile"
        
        remarks = [
            f"A {meal_type} meal featuring {main['item_name']} with {side['item_name']}, perfectly paired with {drink['item_name']}{taste_synergy}.",
            f"Enjoy our {main['item_name']} (popularity: {float(main['popularity_score'])*100:.0f}%) with {side['item_name']}, complemented by {drink['item_name']}.",
            f"Today's special: {main['item_name']} served with {side['item_name']} and {drink['item_name']} - a {meal_type} combination.",
            f"A {meal_type} combination of {main['item_name']}, {side['item_name']}, and {drink['item_name']} (Total: {calorie_total:.0f} kcal).",
            f"Try our {main['item_name']} with {side['item_name']} and {drink['item_name']} - a customer favorite!"
        ]
        return random.choice(remarks)

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
            
        return jsonify({
            'status': 'success',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'combos': combos,
            # 'stats': {
            #     'total_items': {
            #         'mains': len(menu_generator.mains),
            #         'sides': len(menu_generator.sides),
            #         'drinks': len(menu_generator.drinks)
            #     },
            #     'total_combinations': len(menu_generator.used_combinations)
            # }
        })
        
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
