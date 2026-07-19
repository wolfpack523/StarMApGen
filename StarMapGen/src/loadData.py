import re

from JumpLink import JumpLink
from StarSystem import StarSystem

SYSTEM_NAME_PATTERN = re.compile(
    r"^Name:\s*(.*)$"
)

COORDINATE_PATTERN = re.compile(
    r"\((-?\d+),\s*(-?\d+),\s*(-?\d+)\)"
)

STAR_COUNT_PATTERN = re.compile(
    r"^Number of Stars:\s*(\d+)$"
)

SPECTRAL_TYPES_PATTERN = re.compile(
    r"^Spectral Types:\s*(.*)$"
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
):
    """Load star systems and jump links from a DAT file."""

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

            systemMatch = SYSTEM_NAME_PATTERN.match(line)

            if systemMatch:
                system = readSystem(
                    file,
                    params,
                    systemMatch.group(1).strip(),
                )

                systemList.append(system)
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

            print(
                f'Ignoring unsupported data line: "{line}"'
            )

    return systemList


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
        for spectralType in spectralTypesMatch.group(1).split(",")
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


def readRequiredLine(file, description):
    """Read one required line and report truncated DAT files."""

    line = file.readline()

    if line == "":
        raise ValueError(
            f"Unexpected end of file while reading {description}."
        )

    return line
