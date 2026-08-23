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
        TYPE_BARREN: "Barren",
        TYPE_GAS_GIANT: "Gas Giant",
        TYPE_ICE: "Ice World",
        TYPE_OCEAN: "Ocean World",
        TYPE_DESERT: "Desert World",
        TYPE_VOLCANIC: "Volcanic World",
        TYPE_OTHER: "Other",
    }

    def __init__(
            self,
            name="Planet",
            planetType=TYPE_OTHER,
    ):
        self.name = name.strip()

        self.planetType = (
            planetType
            if planetType in self.VALID_TYPES
            else self.TYPE_OTHER
        )

    def getTypeLabel(self):
        return self.TYPE_LABELS.get(
            self.planetType,
            self.planetType,
        )