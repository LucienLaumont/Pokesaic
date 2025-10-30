from src.models import PokemonCard

class PokemonSeries:
    """Represents a Pokémon card series containing multiple PokemonCard objects."""

    def __init__(self, series_dict):
        self.code: str = series_dict["series_code"]
        self.name: str = series_dict["series_name"]
        self.bloc_name : str = series_dict["bloc_name"]
        self.total_cards: int = series_dict["total_cards"]
        self.url : str = series_dict["series_url"]
        self.cards: list[PokemonCard] = PokemonCard.from_list(series_dict["cards"])

    @classmethod
    def from_list(cls, series_list):
        """
        Creates a list of PokemonSeries objects from a list of dictionaries.
        Filters only the 'KSS' series (as per current logic).
        """
        result = []
        for series in series_list:
            result.append(cls(series))
        return result

    def __str__(self):
        return f"PokemonSeries({self.code}, {self.name}, cards: {len(self.cards)})"

    def __repr__(self):
        return self.__str__()
