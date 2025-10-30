import os
from src.pokesaic_generator import PokemonMosaicCreator

KDTREE_PATH = os.path.join("data", "kdtree", "pokemon_kdtree.pkl")
IMAGE_PATH = os.path.join("data","input","nuit_etoile.jpg")

def main():
    pokesaic : PokemonMosaicCreator = PokemonMosaicCreator(kdtree_path=KDTREE_PATH)
    pokesaic.create_mosaic(image_path=IMAGE_PATH,scale=20)

if __name__ == "__main__":
    main()