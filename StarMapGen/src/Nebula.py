class Nebula:
    """A nebula region made up of map grid cells."""

    STYLE_CLOUD = "cloud"
    STYLE_OUTLINE = "outline"
    STYLE_HAZE = "haze"

    VALID_STYLES = {
        STYLE_CLOUD,
        STYLE_OUTLINE,
        STYLE_HAZE,
    }

    def __init__(
            self,
            name="Nebula",
            cells=None,
            style=STYLE_CLOUD,
            color="#7a2f8f",
            opacity=0.35,
    ):
        self.name = name

        self.cells = list(
            cells or []
        )

        self.style = (
            style
            if style in self.VALID_STYLES
            else self.STYLE_CLOUD
        )

        self.color = color

        self.opacity = float(
            opacity
        )

    def addCell(self, x, y):
        """Add a cell if it is not already part of the nebula."""

        cell = (
            int(x),
            int(y),
        )

        if cell not in self.cells:
            self.cells.append(
                cell
            )

    def removeCell(self, x, y):
        """Remove a cell from the nebula."""

        cell = (
            int(x),
            int(y),
        )

        if cell in self.cells:
            self.cells.remove(
                cell
            )

    def containsCell(self, x, y):
        """Return whether a map cell belongs to this nebula."""

        return (
            int(x),
            int(y),
        ) in self.cells

    def getBounds(self):
        """Return the rectangular cell bounds of the nebula."""

        if not self.cells:
            return None

        xValues = [
            x
            for x, y in self.cells
        ]

        yValues = [
            y
            for x, y in self.cells
        ]

        return (
            min(xValues),
            min(yValues),
            max(xValues),
            max(yValues),
        )

    def normalize(self):
        """Remove duplicate cells and keep them in stable order."""

        self.cells = sorted(
            set(self.cells),
            key=lambda cell: (
                cell[1],
                cell[0],
            ),
        )