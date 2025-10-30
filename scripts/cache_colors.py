import os
import json
from typing import List
from src.models import PokemonSeries, PokemonCard

JSON_PATH = os.path.join("data", "json", "pokemon_cards.json")
OUTPUT_PATH = os.path.join("data", "json", "pokemon_cards_labs.json")

def main():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    series_list: List[PokemonSeries] = PokemonSeries.from_list(data)

    # Parcourt les séries et cartes pour enrichir directement `data`
    for series_data, series_obj in zip(data, series_list):
        for card_data, card_obj in zip(series_data["cards"], series_obj.cards):
            color_lab = card_obj.dominant_color_lab
            image_path = card_obj.local_path_sd

            # On enrichit directement le dictionnaire d'origine
            color_lab = [float(x) for x in color_lab]
            card_data["lab_color"] = list(color_lab)
            card_data["image_path"] = image_path

    # Sauvegarde le JSON enrichi
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()