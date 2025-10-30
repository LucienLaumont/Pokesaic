import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from PIL import Image
import numpy as np
from skimage.color import rgb2lab



class PokemonCard:
    """Represents a Pokémon card and computes its dominant color in CIELAB space."""

    def __init__(self, card_dict):
        self.id : str = card_dict["id"]
        self.name: str = card_dict["card_name"]
        self.number: str = card_dict["card_number"]
        self.artist : str = card_dict["artist"]
        self.rarity_level: str = card_dict["rarity_level"]
        self.url_image_sd: str = card_dict["image_sd"]
        self.url_image_hd: str = card_dict["image_hd"]
        self.image_path : str | None = None
        self.image: Image.Image | None = None
        self._dominant_color_lab: tuple | None = None
        self.lab_L: float | None = None
        self.lab_a: float | None = None
        self.lab_b: float | None = None

    # ----------------------
    # IMAGE HANDLING
    # ----------------------

    def download_image(self, quality='sd', force_redownload=False):
        """
        Downloads the image if not already stored locally.
        Stores it in data\\images\\{card_id}.jpg
        """
        if quality == 'sd':
            local_path = self.local_path_sd
        if 'quality' == 'hd':
            local_path = self.local_path_hd

        # Already cached locally
        if os.path.exists(local_path) and not force_redownload:
            try:
                self.image = Image.open(local_path).convert("RGB")
                return self.image
            except Exception as e:
                print(f"Could not open cached {local_path}: {e}")

        # Download if not cached
        try:
            url = self.url_image_sd if quality == 'sd' else self.url_image_hd
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Save to disk
            with open(local_path, "wb") as f:
                f.write(response.content)

            self.image = Image.open(BytesIO(response.content)).convert("RGB")
            return self.image
        
        except Exception as e:
            print(f"Failed to download {self.name}: {e}")
            return None

    # ----------------------
    # COLOR ANALYSIS
    # ----------------------

    def compute_dominant_color_lab(self):
        """Computes dominant color in Lab space from cached image."""
        if self.image is None:
            self.download_image()

        if self.image is None:
            self._dominant_color_lab = (50.0, 0.0, 0.0)
            return self._dominant_color_lab

        try:
            img = self.image.copy()

            w, h = img.size
            margin_x, margin_y = int(w * 0.10), int(h * 0.10)
            img = img.crop((margin_x, margin_y, w - margin_x, h - margin_y))

            arr_rgb = np.array(img, dtype=np.float32) / 255.0
            arr_lab = rgb2lab(arr_rgb)

            if arr_lab.size == 0:
                self._dominant_color_lab = (50.0, 0.0, 0.0)
            else:
                self._dominant_color_lab = tuple(np.mean(arr_lab.reshape(-1, 3), axis=0))

            return self._dominant_color_lab
        
        except Exception as e:
            print(f"Error computing color for {self.name}: {e}")
            self._dominant_color_lab = (50.0, 0.0, 0.0)
            return self._dominant_color_lab

    @property
    def dominant_color_lab(self):
        """Return the cached dominant Lab color (compute if missing)."""
        if self._dominant_color_lab is None:
            color = self.compute_dominant_color_lab()
            self.lab_L, self.lab_a, self.lab_b = color
        return self._dominant_color_lab

    @property
    def local_path_sd(self) -> str:
        """Returns the sanitized local path for the SD image."""
        filename = f"{self.id}_sd.jpg"
        return os.path.join("data\\images", filename)

    @property
    def local_path_hd(self) -> str:
        """Returns the sanitized local path for the HD image."""
        filename = f"{self.id}_hd.jpg"
        return os.path.join("data\\images", filename)
    # ----------------------
    # BULK PROCESSING
    # ----------------------

    @classmethod
    def from_list(cls, cards_data, max_workers=8, pre_download=True):
        """
        Creates multiple PokemonCard objects, optionally pre-downloading images in parallel.

        Args:
            cards_data: list of dicts
            max_workers: number of threads
            pre_download: if True, downloads images in parallel immediately
        """
        cards = [cls(card) for card in cards_data]

        if pre_download:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(card.download_image): card for card in cards}
                for future in as_completed(futures):
                    card = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Download failed for {card.name}: {e}")

        return cards

    def __str__(self):
        return f"PokemonCard({self.name}, {self.number}, Lab: {self._dominant_color_lab})"

    def __repr__(self):
        return self.__str__()