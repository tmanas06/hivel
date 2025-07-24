import pandas as pd
import random
from datetime import datetime

class MenuGenerator:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.df['category'] = self.df['category'].str.lower()

        self.mains = self.df[self.df['category'] == 'main'].to_dict('records')
        self.sides = self.df[self.df['category'] == 'side'].to_dict('records')
        self.drinks = self.df[self.df['category'] == 'drink'].to_dict('records')

        self.used_combinations = set()
        self.usage_count = {
            item['item_name']: 0 for item in self.mains + self.sides + self.drinks
        }

    def generate_combos(self):
        if all(count > 0 for count in self.usage_count.values()):
            self.usage_count = {k: 0 for k in self.usage_count}
            self.used_combinations = set()

        combos = []
        for _ in range(3):
            while True:
                main = min(self.mains, key=lambda x: self.usage_count[x['item_name']])
                side = min(self.sides, key=lambda x: self.usage_count[x['item_name']])
                drink = min(self.drinks, key=lambda x: self.usage_count[x['item_name']])

                combo_key = (main['item_name'], side['item_name'], drink['item_name'])

                if combo_key not in self.used_combinations:
                    self.used_combinations.add(combo_key)
                    self.usage_count[main['item_name']] += 1
                    self.usage_count[side['item_name']] += 1
                    self.usage_count[drink['item_name']] += 1

                    remark = self._generate_remark(main, side, drink)
                    combos.append({
                        'main': main['item_name'],
                        'side': side['item_name'],
                        'drink': drink['item_name'],
                        'remark': remark
                    })
                    break
        return combos

    def _generate_remark(self, main, side, drink):
        total_calories = float(main['calories']) + float(side['calories']) + float(drink['calories'])
        if total_calories > 1000:
            meal_type = "hearty"
        elif total_calories > 700:
            meal_type = "satisfying"
        else:
            meal_type = "light"

        synergy = ""
        if main['taste_profile'] == side['taste_profile'] == drink['taste_profile']:
            synergy = f" with a consistent {main['taste_profile']} profile"

        options = [
            f"A {meal_type} meal of {main['item_name']}, {side['item_name']}, and {drink['item_name']}{synergy}.",
            f"Enjoy {main['item_name']} with {side['item_name']} and {drink['item_name']} — a {meal_type} delight.",
            f"{main['item_name']} + {side['item_name']} + {drink['item_name']} = a perfect {meal_type} combo.",
        ]
        return random.choice(options)

# Run locally
if __name__ == '__main__':
    menu = MenuGenerator("AI_Menu_Recommender_Items.csv")
    combos = menu.generate_combos()
    print("Date:", datetime.now().strftime('%Y-%m-%d'))
    for i, combo in enumerate(combos, 1):
        print(f"\nCombo {i}:")
        print(f"  Main : {combo['main']}")
        print(f"  Side : {combo['side']}")
        print(f"  Drink: {combo['drink']}")
        print(f"  Remark: {combo['remark']}")
