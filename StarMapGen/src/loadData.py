import re

from JumpLink import JumpLink
from Nebula import Nebula
from StarSystem import StarSystem
from Planet import Planet

SYSTEM_NAME_PATTERN = re.compile(
    r"^Name:\s*(.*)$"
)

FACTION_PATTERN = re.compile(
    r'^Faction:\s*"([^"]+)"\s+"([^"]*)"\s*$'
)

COORDINATE_PATTERN = re.compile(
    r"\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)"
)

STAR_COUNT_PATTERN = re.compile(
    r"^Number of Stars:\s*(\d+)$"
)

PLANET_PATTERN = re.compile(
    r'^Planet:\s*'
    r'"([^"]+)"\s+'
    r'"([^"]+)"\s+'
    r'"([^"]+)"'
    r'(?:\s+"([^"]+)")?'
    r'\s*$'
)

SPECTRAL_TYPES_PATTERN = re.compile(
    r"^Spectral Types:\s*(.*)$"
)

NEBULA_NAME_PATTERN = re.compile(
    r"^Nebula:\s*(.*)$"
)

NEBULA_STYLE_PATTERN = re.compile(
    r"^Style:\s*(.*)$"
)

NEBULA_COLOR_PATTERN = re.compile(
    r"^Color:\s*(#[0-9a-fA-F]{6})$"
)

NEBULA_OPACITY_PATTERN = re.compile(
    r"^Opacity:\s*([0-9]*\.?[0-9]+)$"
)

NEBULA_POINTS_PATTERN = re.compile(
    r"^Points:\s*(.*)$"
)

NEBULA_POINT_PATTERN = re.compile(
    r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)"
)

MAP_MINIMUM_PATTERN = re.compile(
    r"^Map Minimum:\s*"
    r"\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)\s*$"
)

MAP_MAXIMUM_PATTERN = re.compile(
    r"^Map Maximum:\s*"
    r"\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)\s*$"
)

# The third quoted value is optional for backwards compatibility.
LINK_PATTERN = re.compile(
    r'^Link:\s*"([^"]+)"\s+"([^"]+)"'
    r'(?:\s+"([^"]+)")?\s*$'
)


def loadData(
        fileName,
        params,
        systemList,
        jumpList,
        nebulaList=None,
):
    """Load map bounds, star systems and jump links from a DAT file."""
    if nebulaList is None:
        nebulaList = []
    declaredMinimum = None
    declaredMaximum = None

    try:
        file = open(
            fileName,
            "r",
            encoding="utf-8",
        )
    except OSError as error:
        raise OSError(
            f'Unable to open data file "{fileName}".'
        ) from error

    with file:
        for rawLine in file:
            line = rawLine.strip()

            if not line:
                continue

            minimumMatch = MAP_MINIMUM_PATTERN.match(line)

            if minimumMatch:
                declaredMinimum = parseCoordinateTriple(
                    minimumMatch
                )
                continue

            maximumMatch = MAP_MAXIMUM_PATTERN.match(line)

            if maximumMatch:
                declaredMaximum = parseCoordinateTriple(
                    maximumMatch
                )
                continue

            systemMatch = SYSTEM_NAME_PATTERN.match(line)

            if systemMatch:
                system = readSystem(
                    file,
                    params,
                    systemMatch.group(1).strip(),
                )

                systemList.append(system)
                continue

            nebulaMatch = NEBULA_NAME_PATTERN.match(
                line
            )

            if nebulaMatch:
                nebula = readNebula(
                    file,
                    nebulaMatch.group(1).strip(),
                )

                nebulaList.append(
                    nebula
                )

                continue

            linkMatch = LINK_PATTERN.match(line)

            if linkMatch:
                startName = linkMatch.group(1)
                endName = linkMatch.group(2)

                status = (
                        linkMatch.group(3)
                        or JumpLink.STATUS_NORMAL
                ).lower()

                if status not in JumpLink.VALID_STATUSES:
                    print(
                        f'Unknown jump status "{status}" '
                        f'for "{startName}" -> "{endName}". '
                        f'Using "{JumpLink.STATUS_NORMAL}".'
                    )

                    status = JumpLink.STATUS_NORMAL

                jumpList.append(
                    JumpLink(
                        startName,
                        endName,
                        status,
                    )
                )

                continue

            planetMatch = PLANET_PATTERN.match(
                line
            )

            if planetMatch:
                systemName = (
                    planetMatch.group(1).strip()
                )

                planetName = (
                    planetMatch.group(2).strip()
                )

                planetType = (
                    planetMatch.group(3)
                    .strip()
                    .lower()
                )

                system = next(
                    (
                        item
                        for item in systemList
                        if item.name == systemName
                    ),
                    None,
                )

                if system is None:
                    print(
                        f'Ignoring planet "{planetName}" because '
                        f'system "{systemName}" does not exist.'
                    )

                    continue

                if planetType not in Planet.VALID_TYPES:
                    print(
                        f'Unknown planet type "{planetType}" '
                        f'for "{planetName}". Using "other".'
                    )

                    planetType = Planet.TYPE_OTHER

                classification = (
                        planetMatch.group(4)
                        or Planet.DEFAULT_CLASSIFICATION
                )

                if classification not in Planet.CLASSIFICATIONS:
                    print(
                        f'Unknown planet classification '
                        f'"{classification}" for "{planetName}". '
                        f'Using "{Planet.DEFAULT_CLASSIFICATION}".'
                    )

                    classification = (
                        Planet.DEFAULT_CLASSIFICATION
                    )

                system.planets.append(
                    Planet(
                        name=planetName,
                        planetType=planetType,
                        classification=classification,
                    )
                )

                continue

            factionMatch = FACTION_PATTERN.match(
                line
            )

            if factionMatch:
                systemName = (
                    factionMatch.group(1).strip()
                )

                faction = (
                    factionMatch.group(2).strip()
                )

                system = next(
                    (
                        item
                        for item in systemList
                        if item.name == systemName
                    ),
                    None,
                )

                if system is None:
                    print(
                        f'Ignoring faction for '
                        f'unknown system "{systemName}".'
                    )

                    continue

                system.faction = faction

                continue

            print(
                f'Ignoring unsupported data line: "{line}"'
            )

    applyMapBounds(
        params,
        systemList,
        declaredMinimum,
        declaredMaximum,
    )

    return systemList


def parseCoordinateTriple(match):
    """Convert the three coordinate groups of a regex match."""

    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
    )


def applyMapBounds(
        params,
        systemList,
        declaredMinimum,
        declaredMaximum,
):
    """Apply stored map bounds or derive them from old DAT files."""

    hasCompleteBounds = (
            declaredMinimum is not None
            and declaredMaximum is not None
    )

    hasIncompleteBounds = (
            declaredMinimum is not None
            or declaredMaximum is not None
    )

    if hasCompleteBounds:
        minimum = declaredMinimum
        maximum = declaredMaximum

        if any(
                minimum[index] > maximum[index]
                for index in range(3)
        ):
            raise ValueError(
                "The map minimum must not be greater "
                "than the map maximum."
            )
    else:
        if hasIncompleteBounds:
            print(
                "The DAT file contains incomplete map bounds. "
                "Deriving the bounds from the star systems."
            )

        minimum, maximum = deriveMapBounds(systemList)

    if systemList:
        actualMinimum, actualMaximum = deriveMapBounds(
            systemList
        )

        expandedMinimum = tuple(
            min(minimum[index], actualMinimum[index])
            for index in range(3)
        )

        expandedMaximum = tuple(
            max(maximum[index], actualMaximum[index])
            for index in range(3)
        )

        if (
                expandedMinimum != minimum
                or expandedMaximum != maximum
        ):
            print(
                "One or more star systems are outside the "
                "stored map bounds. Expanding the map bounds."
            )

        minimum = expandedMinimum
        maximum = expandedMaximum

    params["minX"] = minimum[0]
    params["minY"] = minimum[1]
    params["minZ"] = minimum[2]

    params["maxX"] = maximum[0]
    params["maxY"] = maximum[1]
    params["maxZ"] = maximum[2]


def deriveMapBounds(systemList):
    """Derive the smallest map that contains all star systems."""

    if not systemList:
        return (
            (1, 1, 0),
            (1, 1, 0),
        )

    minimum = (
        min(system.x for system in systemList),
        min(system.y for system in systemList),
        min(system.z for system in systemList),
    )

    maximum = (
        max(system.x for system in systemList),
        max(system.y for system in systemList),
        max(system.z for system in systemList),
    )

    return minimum, maximum


def readSystem(file, params, name):
    """Read the remaining data belonging to one star system."""

    system = StarSystem(
        params,
        generate=False,
    )

    system.name = name

    coordinateLine = readRequiredLine(
        file,
        f'coordinates for "{name}"',
    )

    coordinateMatch = COORDINATE_PATTERN.search(
        coordinateLine
    )

    if coordinateMatch is None:
        raise ValueError(
            f'Invalid coordinates for star system "{name}": '
            f'"{coordinateLine.strip()}"'
        )

    system.x = int(coordinateMatch.group(1))
    system.y = int(coordinateMatch.group(2))
    system.z = int(coordinateMatch.group(3))

    system.mapPos = (
        system.x,
        system.y,
    )

    starCountLine = readRequiredLine(
        file,
        f'star count for "{name}"',
    )

    starCountMatch = STAR_COUNT_PATTERN.match(
        starCountLine.strip()
    )

    if starCountMatch is None:
        raise ValueError(
            f'Invalid star count for star system "{name}": '
            f'"{starCountLine.strip()}"'
        )

    declaredStarCount = int(
        starCountMatch.group(1)
    )

    spectralTypesLine = readRequiredLine(
        file,
        f'spectral types for "{name}"',
    )

    spectralTypesMatch = SPECTRAL_TYPES_PATTERN.match(
        spectralTypesLine.strip()
    )

    if spectralTypesMatch is None:
        raise ValueError(
            f'Invalid spectral types for star system "{name}": '
            f'"{spectralTypesLine.strip()}"'
        )

    system.stars = [
        spectralType.strip()
        for spectralType
        in spectralTypesMatch.group(1).split(",")
        if spectralType.strip()
    ]

    system.nStars = len(system.stars)

    if declaredStarCount != system.nStars:
        print(
            f'Warning: "{name}" declares '
            f"{declaredStarCount} star(s), but contains "
            f"{system.nStars} spectral type(s)."
        )

    return system


def readNebula(
        file,
        name,
):
    """Read the remaining data belonging to one nebula."""

    styleLine = readRequiredLine(
        file,
        f'style for nebula "{name}"',
    )

    styleMatch = NEBULA_STYLE_PATTERN.match(
        styleLine.strip()
    )

    if styleMatch is None:
        raise ValueError(
            f'Invalid style for nebula "{name}": '
            f'"{styleLine.strip()}"'
        )

    style = (
        styleMatch
        .group(1)
        .strip()
        .lower()
    )

    if style not in Nebula.VALID_STYLES:
        raise ValueError(
            f'Unsupported style "{style}" '
            f'for nebula "{name}".'
        )

    colorLine = readRequiredLine(
        file,
        f'color for nebula "{name}"',
    )

    colorMatch = NEBULA_COLOR_PATTERN.match(
        colorLine.strip()
    )

    if colorMatch is None:
        raise ValueError(
            f'Invalid color for nebula "{name}": '
            f'"{colorLine.strip()}"'
        )

    color = (
        colorMatch
        .group(1)
        .lower()
    )

    opacityLine = readRequiredLine(
        file,
        f'opacity for nebula "{name}"',
    )

    opacityMatch = NEBULA_OPACITY_PATTERN.match(
        opacityLine.strip()
    )

    if opacityMatch is None:
        raise ValueError(
            f'Invalid opacity for nebula "{name}": '
            f'"{opacityLine.strip()}"'
        )

    opacity = float(
        opacityMatch.group(1)
    )

    if not 0.0 <= opacity <= 1.0:
        raise ValueError(
            f'Opacity for nebula "{name}" '
            "must be between 0 and 1."
        )

    pointsLine = readRequiredLine(
        file,
        f'points for nebula "{name}"',
    )

    pointsMatch = NEBULA_POINTS_PATTERN.match(
        pointsLine.strip()
    )

    if pointsMatch is None:
        raise ValueError(
            f'Invalid points for nebula "{name}": '
            f'"{pointsLine.strip()}"'
        )

    pointsText = pointsMatch.group(1)

    points = [
        (
            int(match.group(1)),
            int(match.group(2)),
        )
        for match in NEBULA_POINT_PATTERN.finditer(
            pointsText
        )
    ]

    if len(points) < 3:
        raise ValueError(
            f'Nebula "{name}" must contain '
            "at least three boundary points."
        )

    nebula = Nebula(
        name=name,
        points=points,
        style=style,
        color=color,
        opacity=opacity,
    )

    return nebula


def readRequiredLine(file, description):
    """Read one required line and report truncated DAT files."""

    line = file.readline()

    if line == "":
        raise ValueError(
            f"Unexpected end of file while reading {description}."
        )

    return line
