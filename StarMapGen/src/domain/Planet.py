class Planet:
    """A planet belonging to a star system."""

    TYPE_TERRAN = "terran"
    TYPE_BARREN = "barren"
    TYPE_GAS_GIANT = "gas_giant"
    TYPE_ICE = "ice"
    TYPE_OCEAN = "ocean"
    TYPE_DESERT = "desert"
    TYPE_VOLCANIC = "volcanic"
    TYPE_OTHER = "other"

    VALID_TYPES = (
        TYPE_TERRAN,
        TYPE_BARREN,
        TYPE_GAS_GIANT,
        TYPE_ICE,
        TYPE_OCEAN,
        TYPE_DESERT,
        TYPE_VOLCANIC,
        TYPE_OTHER,
    )

    TYPE_LABELS = {
        TYPE_TERRAN: "Terran",
        TYPE_BARREN: "Karg",
        TYPE_GAS_GIANT: "Gasriese",
        TYPE_ICE: "Eiswelt",
        TYPE_OCEAN: "Ozeanwelt",
        TYPE_DESERT: "Wüstenwelt",
        TYPE_VOLCANIC: "Vulkanwelt",
        TYPE_OTHER: "Sonstiges",
    }

    CLASSIFICATIONS = (
        "Agrarwelt",
        "Bergwerksplanet",
        "Bibliothekswelt",
        "Dschungelplanet",
        "Eiswelt",
        "Fabrikwelt",
        "Festungswelt",
        "Feudalwelt",
        "Forschungsstation",
        "Gartenwelt",
        "Grenzwelt",
        "Höhlenwelt",
        "Industriewelt",
        "Leblose Welt",
        "Makropolwelt",
        "Munitorumswelt",
        "Nachtwelt",
        "Ordenswelt",
        "Ozeanwelt",
        "Ritterwelt",
        "Schreinwelt",
        "Todeswelt",
        "Trophäenwelt",
        "Urzeitwelt",
        "Waldplanet",
        "Wüstenplanet",
        "Zivilisierte Welt",
        "Dämonenwelt",
        "Exoditenwelt",
        "Gasriese",
        "Gruftwelt",
        "Hexenwelt",
        "Jungfernwelt",
        "Orkwelten",
        "Tauwelten",
        "Weltenschiff",
        "Sonstige Welt",
    )

    DEFAULT_CLASSIFICATION = "Sonstige Welt"

    def __init__(
            self,
            name="Planet",
            planetType=TYPE_OTHER,
            classification=DEFAULT_CLASSIFICATION,
    ):
        self.name = name.strip()

        self.planetType = (
            planetType
            if planetType in self.VALID_TYPES
            else self.TYPE_OTHER
        )

        self.classification = (
            classification
            if classification in self.CLASSIFICATIONS
            else self.DEFAULT_CLASSIFICATION
        )

    def getTypeLabel(self):
        return self.TYPE_LABELS.get(
            self.planetType,
            self.planetType,
        )
