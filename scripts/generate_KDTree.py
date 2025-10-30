import os
from src.KDTree_generator import PokemonColorKDTree

JSON_PATH = os.path.join("data", "json", "pokemon_cards_labs.json")
OUTPUT_PATH = os.path.join("data", "kdtree","pokemon_kdtree.pkl")

def main():
    kdtree : PokemonColorKDTree = PokemonColorKDTree(json_path=JSON_PATH)
    kdtree.load_data()
    kdtree.build_kdtree()
    kdtree.save_kdtree(output_path=OUTPUT_PATH)

if __name__ == "__main__":
    main()