class Nebula:
    """A nebula region made up of map grid cells."""

    STYLE_CLOUD = "cloud"
    STYLE_OUTLINE = "outline"
    STYLE_HAZE = "haze"

    VALID_STYLES = (
        STYLE_CLOUD,
        STYLE_OUTLINE,
        STYLE_HAZE,
    )

    def __init__(
            self,
            name="Nebula",
            cells=None,
            style=STYLE_CLOUD,
            color="#7a2f8f",
            opacity=0.35,
    ):
        self.name = name
        self.cells = list(cells or [])

        self.style = (
            style
            if style in self.VALID_STYLES
            else self.STYLE_CLOUD
        )

        self.color = color
        self.opacity = float(opacity)

    def addCell(self, x, y):
        """Add one map cell."""

        cell = (
            int(x),
            int(y),
        )

        if cell not in self.cells:
            self.cells.append(cell)

    def removeCell(self, x, y):
        """Remove one map cell."""

        cell = (
            int(x),
            int(y),
        )

        if cell in self.cells:
            self.cells.remove(cell)

    def containsCell(self, x, y):
        """Return whether the nebula contains a cell."""

        return (
            int(x),
            int(y),
        ) in self.cells

    def normalize(self):
        """Remove duplicates and sort cells by Y and X."""

        self.cells = sorted(
            set(self.cells),
            key=lambda cell: (
                cell[1],
                cell[0],
            ),
        )