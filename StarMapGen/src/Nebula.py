class Nebula:
    """A nebula defined by an ordered polygon."""

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
            points=None,
            style=STYLE_CLOUD,
            color="#7a2f8f",
            opacity=0.35,
    ):
        self.name = name
        self.points = list(points or [])

        self.style = (
            style
            if style in self.VALID_STYLES
            else self.STYLE_CLOUD
        )

        self.color = color
        self.opacity = float(opacity)

    def addPoint(self, x, y):
        """Add one boundary point."""

        point = (
            int(x),
            int(y),
        )

        if point not in self.points:
            self.points.append(point)

    def removePoint(self, x, y):
        """Remove one boundary point."""

        point = (
            int(x),
            int(y),
        )

        if point in self.points:
            self.points.remove(point)

    def containsPoint(self, x, y):
        """Return whether the nebula contains a boundary point."""

        return (
            int(x),
            int(y),
        ) in self.points