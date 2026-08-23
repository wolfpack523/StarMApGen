#!/usr/bin/env python
from JumpLink import JumpLink
from StarSystem import StarSystem
from math import sqrt, atan, acos, sin, cos, fabs

p2mm = 0.26458333333  # /25.4/96

JUMP_STATUS_STYLES = {
    JumpLink.STATUS_NORMAL: {
        "color": "#ffffff",
        "strokeWidth": 5,
        "dash": None,
    },
    JumpLink.STATUS_CAUTION: {
        "color": "#ffd43b",
        "strokeWidth": 5,
        "dash": (12, 8),
    },
    JumpLink.STATUS_DANGEROUS: {
        "color": "#ff7a00",
        "strokeWidth": 7,
        "dash": None,
    },
    JumpLink.STATUS_BLOCKED: {
        "color": "#ff3b30",
        "strokeWidth": 6,
        "dash": (4, 7),
    },
    JumpLink.STATUS_LOST: {
        "color": "#0033cc",
        "strokeWidth": 6,
        "dash": (4, 7),
    },
}


def createDef(spType, starData, dDict):
    """Create the gradient definitions for the star symbols

    Each star symbol consists of three components that each is
    a unique color and gradient.  The colors are based on the
    spectral type of the star but the gradients are the same
    regardless of spectral type.  This function creates the gradient
    information and returns the gradient names to be used.

    To help minimize the size of the resultant SVG file, gradients
    are only generated for the spectral types that will be on the
    map.  The gradients are stored in a dictionary, indexed by
    an ID based on the spectral type of the star.  This dictionary
    is passed in as one of the parameters and if the requested
    gradient is already there, the function simply returns the list
    of gradients to use for the specified star.

    Inputs:
     - spType - The spectral type of the star
     - starData - A list containing information about the size of
                  the star symbol and the colors to be used
     - dDict - the definition dictionary that will hold the
               definition information

    Outputs:
     - gList - a list of the three gradients needed for the
               specified star.
    """
    g1 = "rg" + spType + "a"
    g2 = "rg" + spType + "b"
    g3 = "rg" + spType + "c"

    gList = [g1, g2, g3]
    if g1 not in dDict:
        color = interpolateColors(spType, 0)
        #		print ("Adding " + g1 + " definition")
        r1 = 100 * starData[0]
        s1 = '  <radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="%f">\n' % (g1, r1)
        s1 += '   <stop stop-color="%s" offset="0"/>\n' % (color)
        s1 += '   <stop stop-color="%s" stop-opacity="0" offset="1"/>\n' % (color)
        s1 += '  </radialGradient>\n'
        dDict[g1] = s1

    if g2 not in dDict:
        color = interpolateColors(spType, 1)
        #		print ("Adding " + g2 + " definition")
        r2 = 56.25 * starData[0]
        s2 = '  <radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="%f">\n' % (g2, r2)
        s2 += '   <stop stop-color="%s" offset="0"/>\n' % (color)
        s2 += '   <stop stop-color="%s" offset="0.54545"/>\n' % (color)
        s2 += '   <stop stop-color="%s" stop-opacity="0" offset="1"/>\n' % (color)
        s2 += '  </radialGradient>\n'
        dDict[g2] = s2

    if g3 not in dDict:
        color = interpolateColors(spType, 2)
        #		print ("Adding " + g3 + " definition")
        r3 = 50 * starData[0]
        s3 = '  <radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="%f">\n' % (g3, r3)
        s3 += '   <stop stop-color="%s" offset="0"/>\n' % (color)
        s3 += '   <stop stop-color="%s" stop-opacity=".86432" offset="0.5"/>\n' % (color)
        s3 += '   <stop stop-color="%s" stop-opacity="0" offset="1"/>\n' % (color)
        s3 += '  </radialGradient>\n'
        dDict[g3] = s3

    return gList


def interpolateColors(sp, index):
    spVal = specTypeToValue(sp)
    (low, high) = getBracketValues(spVal)
    val = spVal % 10
    lParams = getParams2(low)
    hParams = getParams2(high)
    c1 = lParams[1][index]
    c2 = hParams[1][index]
    r1 = int(c1[1:3], 16)
    r2 = int(c2[1:3], 16)
    g1 = int(c1[3:5], 16)
    g2 = int(c2[3:5], 16)
    b1 = int(c1[5:7], 16)
    b2 = int(c2[5:7], 16)
    r = hex(r1 + (r2 - r1) // 10 * val)
    g = hex(g1 + (g2 - g1) // 10 * val)
    b = hex(b1 + (b2 - b1) // 10 * val)
    color = "#" + r[2:4] + g[2:4] + b[2:4]
    if (len(color) == 6): color += "0"
    return color


def createSymbol(p, spType, pos, dDict):
    scale = p['scale'] * p2mm
    spVal = specTypeToValue(spType)
    starData = getParams2(spVal)
    starData[0] = getSize(spVal)
    gList = createDef(spType, starData, dDict)
    s = ' <g transform="matrix(%f,0,0,%f,%f,%f)">\n' % (scale, scale, starData[0] * pos[0] * scale,
                                                        starData[0] * pos[1] * scale)
    if ("NS" == spType or "BH" == spType):
        s += '  <path style="fill:#ffffff;" d="m -4,-40 a 6.35,54.2 0 0 1 7,-7.5 l -2.8,48.5 z" transform="matrix(-0.8,0.6,-0.6,-0.8,0,0)" />'
        scale = 1
    s += '  <circle r="%f" fill="black"/>\n' % (starData[0] * 55.)
    s += '  <circle r="%f" fill="url(#%s)"/>\n' % (starData[0] * 100., gList[0])
    s += '  <circle r="%f" fill="url(#%s)"/>\n' % (starData[0] * 75., gList[1])
    s += '  <circle r="%f" fill="url(#%s)"/>\n' % (starData[0] * 50., gList[2])
    if ("NS" == spType or "BH" == spType):
        s += '  <path style="fill:#ffffff;" d="m -4,-40 a 6.35,54.2 0 0 1 7,-7.5 l -2.8,48.5 z" transform="matrix(0.8,-0.6,0.6,0.8,0,0)" />'
    s += ' </g>\n'
    return s


def getParams(spType):
    return {
        'O0': [0.75, ["#5579ff", "#1345ff", "#9cb2ff"]],  # TODO currently using B0 colors, get unique
        'B0': [0.75, ["#5579ff", "#1345ff", "#9cb2ff"]],
        'A0': [0.5, ["#688bff", "#2256ff", "#b9c9ff"]],
        'F0III': [0.75, ["#9cb2ff", "#607aff", "#e0e4ff"]],
        'G0III': [0.75, ["#fffcb6", "#fffa72", "#fff8fc"]],
        'K0III': [0.75, ["#ffc58d", "#ff9228", "#ffeedd"]],
        'M0III': [0.75, ["#ff9f41", "#ff7e00", "#ffc38b"]],
        'F0I': [1, ["#9cb2ff", "#607aff", "#e0e4ff"]],
        'G0I': [1, ["#fffcb6", "#fffa72", "#fff8fc"]],
        'K0I': [1, ["#ffc58d", "#ff9228", "#ffeedd"]],
        'M0I': [1, ["#ff9f41", "#ff7e00", "#ffc38b"]],
        'F0': [0.5, ["#9cb2ff", "#607aff", "#e0e4ff"]],
        'G0': [0.5, ["#fffcb6", "#fffa72", "#fff8fc"]],
        'K0': [0.5, ["#ffc58d", "#ff9228", "#ffeedd"]],
        'M0': [0.25, ["#ff9f41", "#ff7e00", "#ffc38b"]],
        'BD': [0.20, ["#ff26b0", "#ff4000", "#ff64c8"]],
        'WD': [0.25, ["#5579ff", "#1345ff", "#9cb2ff"]],
        'NS': [0.375, ["#c86400", "#804000", "#ff8000"]],
        'BH': [0.375, ["#0000ff", "#ff0000", "#000000"]],
    }.get(spType, [0.25, ["rgM0a", "rgM0b", "rgM0c"]]);


def getParams2(spType):
    return {
        500: [0.75, ["#5579ff", "#1345ff", "#9cb2ff"]],  # O0V #TODO currently using B0 colors, get unique
        510: [0.75, ["#5579ff", "#1345ff", "#9cb2ff"]],  # B0V
        520: [0.5, ["#688bff", "#2256ff", "#b9c9ff"]],  # A0V
        330: [0.75, ["#9cb2ff", "#607aff", "#e0e4ff"]],  # F0III
        340: [0.75, ["#fffcb6", "#fffa72", "#fff8fc"]],  # G0III
        350: [0.75, ["#ffc58d", "#ff9228", "#ffeedd"]],  # K0III
        360: [0.75, ["#ff9f41", "#ff7e00", "#ffc38b"]],  # M0III
        370: [0.75, ["#ff6040", "#ff4000", "#ff8030"]],  # L0III (not real but needed for extrapolation)
        130: [1, ["#9cb2ff", "#607aff", "#e0e4ff"]],  # F0I
        140: [1, ["#fffcb6", "#fffa72", "#fff8fc"]],  # G0I
        150: [1, ["#ffc58d", "#ff9228", "#ffeedd"]],  # K0I
        160: [1, ["#ff9f41", "#ff7e00", "#ffc38b"]],  # M0I
        170: [1, ["#ff6040", "#ff4000", "#ff8030"]],  # L0I (not real but needed for extrapolation)
        530: [0.5, ["#9cb2ff", "#607aff", "#e0e4ff"]],  # F0V
        540: [0.5, ["#fffcb6", "#fffa72", "#fff8fc"]],  # G0V
        550: [0.5, ["#ffc58d", "#ff9228", "#ffeedd"]],  # K0V
        560: [0.25, ["#ff9f41", "#ff7e00", "#ffc38b"]],  # M0V
        570: [0.20, ["#ff6040", "#ff4000", "#ff8030"]],  # L0V
        580: [0.20, ["#ff26b0", "#ff4000", "#ff64c8"]],  # BD
        600: [0.25, ["#5579ff", "#1345ff", "#9cb2ff"]],  # WD
        700: [0.375, ["#c86400", "#804000", "#ff8000"]],  # NS
        800: [0.375, ["#0000ff", "#ff0000", "#000000"]],  # BH
    }.get(spType, [0.25, ["rgM0a", "rgM0b", "rgM0c"]]);


def specTypeToValue(sp):
    if ("BD" == sp): return 580
    if ("WD" == sp): return 600
    if ("NS" == sp): return 700
    if ("BH" == sp): return 800
    specOrder = ["O", "B", "A", "F", "G", "K", "M"]
    type = 10 * specOrder.index(sp[0:1])
    type += int(sp[1:2])
    spClass = sp[2:]
    if ("" == spClass): return type + 500
    if ("III" == spClass): return type + 300
    if ("I" == spClass): return type + 100
    if ("II" == spClass): return type + 200
    if ("IV" == spClass): return type + 400


def getSize(spVal):
    val = spVal // 10 * 10
    p = getParams2(val)
    return p[0]


def getBracketValues(spVal):
    if (spVal >= 570): return (spVal, spVal)
    low = int(spVal) // 10 * 10
    return (low, low + 10)


def sortSpecTypeForDisplay(st):
    if ("BD" == st): return 2000
    if ("WD" == st): return 1000
    return specTypeToValue(st)


# rank = {
#	#supergiants
#       'F0I': 30,
#       'G0I': 40,
#       'K0I': 50,
#       'M0I': 60,
#       #giants
#       'F0III': 130,
#       'G0III': 140,
#       'K0III': 150,
#       'M0III': 160,
#       #main sequence
#       'O0': 110,
#       'B0': 120,
#       'A0': 220,
#       'F0': 230,
#       'G0': 240,
#       'K0': 250,
#       'M0': 500,
#	'M5': 550,
#       #brown dwarfs
#       'BD': 2000,
#       #collapsars
#       'WD': 1000,
#       'NS': 400,
#       'BH': 410,
#   }
# return rank[st]

def writeDefs(f, dDict):
    f.write(" <defs>\n")
    for x in dDict:
        f.write(dDict[x])
    f.write(" </defs>\n")


def writeSymbols(f, sList):
    for x in sList:
        f.write(x)


def createSystems(p):
    """Create randomly generated star systems."""

    minX = p.get("minX", 1)
    minY = p.get("minY", 1)

    mapWidth = p["maxX"] - minX + 1
    mapHeight = p["maxY"] - minY + 1
    mapDepth = p["maxZ"] - p["minZ"] + 1

    volume = (
            mapWidth
            * mapHeight
            * mapDepth
    )

    nStars = int(
        round(
            volume * p["stellarDensity"]
        )
    )

    systemList = []

    for _ in range(nStars):
        systemList.append(
            StarSystem(p)
        )

    return systemList


def findOverlaps(sList):
    mList = []
    mulList = []
    for x in sList:
        mList.append(x.mapPos)
    for x in mList:
        n = mList.count(x);
        if (n > 1 and not x in mulList):
            mulList.append(x)
            print("there are", n, "systems at", x)
    return mulList


def getTweakOffset(sList):
    offset = (0, 0)
    largeStarCount = 0
    for s in sList:
        if (sortSpecTypeForDisplay(s) < 560):
            largeStarCount = largeStarCount + 1
    nStars = len(sList)
    t1 = (getStarOffsetList(nStars))[0]
    temp = (0.5 * t1[0], 0.5 * t1[1])

    if (1 == largeStarCount and nStars < 5):
        offset = (-temp[0], -temp[1])

    if (2 == largeStarCount and (3 == nStars or 4 == nStars)):
        offset = (0, -temp[1])

    if (3 == largeStarCount and (5 == nStars or 4 == nStars)):
        offset = (0, -temp[1])

    if (4 == nStars and largeStarCount < 3):
        offset = (-0.5 * temp[0], -0.5 * temp[1])

    if (nStars > 5 and 1 == largeStarCount):
        offset = (-0.5 * temp[0], -0.5 * temp[1])

    if (nStars > 7 and (2 == largeStarCount or 4 == largeStarCount or 5 == largeStarCount)):
        offset = (-0.5 * temp[0], -0.5 * temp[1])

    if ((6 == nStars or 7 == nStars) and 2 == largeStarCount):
        offset = (0, -0.5 * temp[1])

    if ((6 == nStars or 7 == nStars) and 3 == largeStarCount):
        offset = (temp[0], -0.5 * temp[1])

    if ((6 == nStars or 7 == nStars) and (4 == largeStarCount or 5 == largeStarCount)):
        offset = (temp[0], 0)

    if (nStars > 7 and 3 == largeStarCount):
        offset = (temp[0], -0.5 * temp[1])

    if (nStars > 7 and (6 == largeStarCount or 7 == largeStarCount)):
        offset = (-0.5 * temp[0], 0)

    return offset


def createMapSymbols(
        p,
        systemList,
        mList,
        defDict,
):
    symbolList = []
    dupList = {}

    systemOffsets = [
        (0, 0),
        (-30, 30),
        (30, -30),
        (-30, -30),
        (30, 30),
    ]

    minX = p.get("minX", 1)
    minY = p.get("minY", 1)

    for system in systemList:
        tweakOffset = (0, 0)
        dupCount = 0

        # Handle multiple star systems at the same absolute
        # X/Y coordinate.
        if system.mapPos in mList:
            if system.mapPos in dupList:
                dupCount = (
                        dupList[system.mapPos] + 1
                )
            else:
                dupCount = 1

            dupList[system.mapPos] = dupCount

        starOffset = [(0, 0)]

        if system.nStars > 1:
            starOffset = getStarOffsetList(
                system.nStars
            )

            tweakOffset = getTweakOffset(
                system.stars
            )

        # Translate absolute map coordinates into coordinates
        # relative to the current map minimum.
        localX = (
                system.mapPos[0]
                - minX
                + 1
        )

        localY = (
                system.mapPos[1]
                - minY
                + 1
        )

        xPos = (
                localX * 150
                + systemOffsets[dupCount][0]
                + tweakOffset[0]
        )

        yPos = (
                localY * 150
                + systemOffsets[dupCount][1]
                + tweakOffset[1]
        )

        data = (
                '<g transform="translate(%f,%f)">'
                % (
                    xPos * p2mm,
                    yPos * p2mm,
                )
        )

        # Keep track of the system centre for jump lines and names.
        system.drawnPos = (
            xPos - tweakOffset[0],
            yPos - tweakOffset[1],
        )

        stars = sorted(
            system.stars,
            key=sortSpecTypeForDisplay,
        )

        for index, star in enumerate(stars):
            data += createSymbol(
                p,
                star,
                starOffset[index],
                defDict,
            )

        if p["printZ"]:
            height = 30

            data += (
                    '<text x="%f" y="%f" font-size="%d" '
                    'font-family="Arial,Helvetica,sans-serif" '
                    'fill="white">'
                    % (
                        20 * p["scale"] * p2mm,
                        height * p["scale"] * p2mm,
                        height * p2mm,
                    )
            )

            if system.z > 0:
                data += "+"

            data += "%d</text>" % system.z

        data += "</g>"
        symbolList.append(data)

    return symbolList


def getStarOffsetList(n):
    """Offsets for stars in a system

    This method returns a list of tuples based on the number of stars
    in the system.  Each tuple represents the x,y offset of the star
    from the system center for drawing purposes.

    Input: n - the number of stars in the system

    Output: a list of x,y pairs, one for each star in the system
    """
    if (2 == n):
        return [(-24, -24), (24, 24)]
    if (3 == n):
        return [(-36, -36), (36, -20), (-12, 36)]
    if (4 == n):
        print("4 stars")
        return [(-36, -36), (36, -36), (-36, 36), (36, 36)]
    if (5 == n):
        print("5 stars")
        return [(-44, -20), (0, -48), (44, -20), (28, 32), (-28, 32)]
    if (6 == n):
        print("6 stars")
        return [(-28, -48), (28, -48), (56, 0), (28, 48), (-28, 48), (-56, 0)]
    if (7 == n):
        print("7 stars")
        return [(-28, -48), (28, -48), (56, 0), (28, 48), (-28, 48), (-56, 0), (0, 0)]
    if (8 == n):
        print("8 stars")
        return [(-42, -42), (0, -60), (42, -42), (60, 0), (42, 42), (0, 60), (-42, 42), (-60, 0)]
    if (9 == n):
        print("9 stars")
        return [(-42, -42), (0, -60), (42, -42), (60, 0), (42, 42), (0, 60), (-42, 42), (-60, 0), (0, 0)]
    if (10 == n):
        print("10 stars")
        return [(-42, -42), (0, -60), (42, -42), (60, 0), (42, 42), (0, 60), (-42, 42), (-60, 0), (20, -20), (-20, 20)]
    else:
        return [(0, 0) * n]


def writeMapHeader(f, w, h):
    """Write a clean, standards-compliant SVG header."""

    f.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
    )

    f.write(
        '<svg '
        'xmlns="http://www.w3.org/2000/svg" '
        'version="1.1" '
        f'viewBox="0 0 {w:.6f} {h:.6f}" '
        f'width="{w:.6f}" '
        f'height="{h:.6f}" '
        'preserveAspectRatio="xMidYMid meet">'
        '\n'
    )


def findConnections(systemList, jumpList):
    """Create drawable connection data from JumpLink objects."""

    connectionList = []

    systemsByName = {
        system.name: system
        for system in systemList
    }

    for jump in jumpList:
        # Transitional fallback in case an old tuple still exists
        # somewhere in memory.
        if isinstance(jump, JumpLink):
            startName = jump.startName
            endName = jump.endName
            status = jump.status
        else:
            try:
                startName = jump[0]
                endName = jump[1]
            except (IndexError, TypeError):
                print(
                    f"Ignoring invalid jump link: {jump}"
                )
                continue

            status = JumpLink.STATUS_NORMAL

        startSystem = systemsByName.get(startName)
        endSystem = systemsByName.get(endName)

        if startSystem is None or endSystem is None:
            print(
                f'Ignoring jump link "{startName}" -> '
                f'"{endName}" because a system is missing.'
            )
            continue

        if startSystem is endSystem:
            print(
                f'Ignoring self-link for "{startName}".'
            )
            continue

        deltaX = startSystem.x - endSystem.x
        deltaY = startSystem.y - endSystem.y
        deltaZ = startSystem.z - endSystem.z

        distance = int(
            sqrt(
                deltaX * deltaX
                + deltaY * deltaY
                + deltaZ * deltaZ
            )
            + 0.5
        )

        connectionList.append(
            (
                startSystem.drawnPos,
                endSystem.drawnPos,
                distance,
                status,
            )
        )

    return connectionList


def findJumps(systemList):
    """Generate normal jump links between nearby habitable systems."""

    jumpList = []

    habitableSystems = [
        system
        for system in systemList
        if system.hasHabitable()
    ]

    for firstIndex in range(
            len(habitableSystems)
    ):
        for secondIndex in range(
                firstIndex + 1,
                len(habitableSystems),
        ):
            firstSystem = habitableSystems[firstIndex]
            secondSystem = habitableSystems[secondIndex]

            deltaX = firstSystem.x - secondSystem.x
            deltaY = firstSystem.y - secondSystem.y
            deltaZ = firstSystem.z - secondSystem.z

            distance = int(
                sqrt(
                    deltaX * deltaX
                    + deltaY * deltaY
                    + deltaZ * deltaZ
                )
                + 0.5
            )

            if distance < 15:
                jumpList.append(
                    JumpLink(
                        firstSystem.name,
                        secondSystem.name,
                        JumpLink.STATUS_NORMAL,
                    )
                )

    return jumpList


def drawConnections(params, file, connectionList):
    """Draw jump links using their configured route status."""

    for connection in connectionList:
        startPosition = connection[0]
        endPosition = connection[1]
        distance = connection[2]

        status = (
            connection[3]
            if len(connection) > 3
            else JumpLink.STATUS_NORMAL
        )

        style = JUMP_STATUS_STYLES.get(
            status,
            JUMP_STATUS_STYLES[
                JumpLink.STATUS_NORMAL
            ],
        )

        color = style["color"]

        strokeWidth = (
                style["strokeWidth"]
                * p2mm
        )

        styleParts = [
            f"stroke:{color}",
            f"stroke-width:{strokeWidth:f}",
            "fill:none",
        ]

        dash = style["dash"]

        if dash is not None:
            dashArray = ",".join(
                f"{value * p2mm:f}"
                for value in dash
            )

            styleParts.append(
                f"stroke-dasharray:{dashArray}"
            )

        lineStyle = "; ".join(styleParts)

        data = (
            f'<g data-jump-status="{status}">'
            f'<line style="{lineStyle}"'
        )

        data += (
                ' x1="%f" y1="%f" x2="%f" y2="%f" />\n'
                % (
                    startPosition[0] * p2mm,
                    startPosition[1] * p2mm,
                    endPosition[0] * p2mm,
                    endPosition[1] * p2mm,
                )
        )

        offset = (-45.0, -45.0)
        xScale = 0.0
        yScale = 0.0
        slope = 0.0
        angle = 0.0

        x1 = float(startPosition[0])
        x2 = float(endPosition[0])
        y1 = float(startPosition[1])
        y2 = float(endPosition[1])

        if x1 != x2:
            slope = (y1 - y2) / (x2 - x1)
            angle = atan(-slope) * 180 / acos(-1.0)

            xScale = sin(
                atan(slope) * 2
            )

            yScale = cos(
                atan(slope) * 2
            )

            if fabs(angle) >= 45.0:
                xScale = -xScale

            if slope < 0:
                xScale = -xScale
        else:
            xScale = -0.2
            yScale = 0

        if slope == 0:
            yScale /= 2
        elif fabs(angle) < 10:
            yScale *= 0.8

        xMiddle = (
                          startPosition[0] + endPosition[0]
                  ) / 2 + xScale * offset[0]

        yMiddle = (
                          startPosition[1] + endPosition[1]
                  ) / 2 + yScale * offset[1]

        data += (
                '<text x="%f" y="%f" font-size="%f" '
                'font-family="Arial,Helvetica,sans-serif" '
                'fill="%s">'
                % (
                    xMiddle * p2mm,
                    yMiddle * p2mm,
                    40 * params["scale"] * p2mm,
                    color,
                )
        )

        data += (
            f"{distance}</text></g>\n"
        )

        file.write(data)


def writeNames(p, f, sList):
    '''This adds in the names of the star systems.
    Right now it just draws them to the upper left of the
    star's symbol'''
    offset = p['scale'] * 25
    for s in sList:
        data = '<g><text x="%f" y="%f" font-size="%f"' % ((s.drawnPos[0] + offset) * p2mm,
                                                          (s.drawnPos[1] - offset) * p2mm, 50 * p['scale'] * p2mm)
        data += ' font-family="Arial, Helvetica, sans-serif" fill="white">'
        data += "%s</text></g>\n" % s.name
        f.write(data)

def writeNebulae(
        params,
        file,
        nebulaList,
):
    """Draw all nebulae below the map grid."""

    if not nebulaList:
        return

    file.write(
        '<g id="nebulae">\n'
    )

    for index, nebula in enumerate(
            nebulaList
    ):
        writeNebula(
            params,
            file,
            nebula,
            index,
        )

    file.write(
        "</g>\n"
    )


def writeNebula(
        params,
        file,
        nebula,
        index,
):
    """Draw one nebula polygon."""

    if len(nebula.points) < 3:
        return

    points = getNebulaSvgPoints(
        params,
        nebula,
    )

    pointText = formatNebulaPoints(
        points
    )

    file.write(
        f'<g id="nebula-{index}" '
        f'data-nebula-name="{escapeSvgAttribute(nebula.name)}" '
        f'data-nebula-style="{nebula.style}">\n'
    )

    if nebula.style == "outline":
        file.write(
            '<polygon '
            f'points="{pointText}" '
            'fill="none" '
            f'stroke="{nebula.color}" '
            f'stroke-opacity="{nebula.opacity:f}" '
            f'stroke-width="{6 * p2mm:f}" '
            'stroke-linejoin="round" '
            '/>\n'
        )

    elif nebula.style == "haze":
        file.write(
            '<polygon '
            f'points="{pointText}" '
            f'fill="{nebula.color}" '
            f'fill-opacity="{nebula.opacity * 0.55:f}" '
            f'stroke="{nebula.color}" '
            f'stroke-opacity="{nebula.opacity * 0.35:f}" '
            f'stroke-width="{10 * p2mm:f}" '
            'stroke-linejoin="round" '
            '/>\n'
        )

    else:
        file.write(
            '<polygon '
            f'points="{pointText}" '
            f'fill="{nebula.color}" '
            f'fill-opacity="{nebula.opacity:f}" '
            'stroke="none" '
            '/>\n'
        )

    file.write(
        "</g>\n"
    )

def getNebulaSvgPoints(
        params,
        nebula,
):
    """Convert nebula map points to SVG coordinates."""

    minX = params.get(
        "minX",
        1,
    )

    minY = params.get(
        "minY",
        1,
    )

    svgPoints = []

    for x, y in nebula.points:
        localX = (
                x
                - minX
                + 1
        )

        localY = (
                y
                - minY
                + 1
        )

        svgX = (
                localX
                * 150
                * p2mm
        )

        svgY = (
                localY
                * 150
                * p2mm
        )

        svgPoints.append(
            (
                svgX,
                svgY,
            )
        )

    return svgPoints

def formatNebulaPoints(points):
    """Format SVG polygon points."""

    return " ".join(
        f"{x:f},{y:f}"
        for x, y in points
    )

def escapeSvgAttribute(value):
    """Escape text used inside an SVG attribute."""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )

def createMap(
        params,
        defDict,
        symbolList,
        connectionList,
        starList,
        nebulaList=None,
):
    if nebulaList is None:
        nebulaList = []

    minX = params.get("minX", 1)
    minY = params.get("minY", 1)

    mapWidth = (
            params["maxX"]
            - minX
            + 1
    )

    mapHeight = (
            params["maxY"]
            - minY
            + 1
    )

    width = (
            (mapWidth + 1)
            * 150
            * p2mm
    )

    height = (
            (mapHeight + 1)
            * 150
            * p2mm
    )

    with open(
            params["filename"],
            "w",
            encoding="utf-8",
    ) as file:
        writeMapHeader(
            file,
            width,
            height,
        )

        writeDefs(
            file,
            defDict,
        )

        file.write(
            '<g id="background" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Background">\n'
        )

        file.write(
            ' <rect '
            f'height="{height:f}" '
            f'width="{width:f}" '
            'y="0" x="0" fill="#000"/>\n'
        )

        file.write("</g>\n")

        writeNebulae(
            params,
            file,
            nebulaList,
        )

        file.write(
            '<g id="grid" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Grid">\n'
        )

        xMin = 75
        yMin = 75

        xMax = (
                mapWidth * 150
                + 75
        )

        yMax = (
                mapHeight * 150
                + 75
        )

        for index in range(mapWidth + 1):
            x = (
                    index * 150
                    + 75
            )

            code = (
                    '<line '
                    'x1="%f" y1="%f" '
                    'x2="%f" y2="%f" '
                    'style="stroke:rgb(100,100,100); '
                    'stroke-width:%f" />\n'
                    % (
                        x * p2mm,
                        yMin * p2mm,
                        x * p2mm,
                        yMax * p2mm,
                        3 * p2mm,
                    )
            )

            file.write(code)

        for index in range(mapHeight + 1):
            y = (
                    index * 150
                    + 75
            )

            code = (
                    '<line '
                    'x1="%f" y1="%f" '
                    'x2="%f" y2="%f" '
                    'style="stroke:rgb(100,100,100); '
                    'stroke-width:%f" />\n'
                    % (
                        xMin * p2mm,
                        y * p2mm,
                        xMax * p2mm,
                        y * p2mm,
                        3 * p2mm,
                    )
            )

            file.write(code)

        file.write("</g>\n")

        file.write(
            '<g id="jumps" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Jumps">\n'
        )

        drawConnections(
            params,
            file,
            connectionList,
        )

        file.write("</g>\n")

        file.write(
            '<g id="stars" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Stars">\n'
        )

        writeSymbols(
            file,
            symbolList,
        )

        file.write("</g>\n")

        file.write(
            '<g id="names" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Names">\n'
        )

        writeNames(
            params,
            file,
            starList,
        )

        file.write("</g>\n")
        file.write("</svg>")


if __name__ == '__main__':
    #	seed(3)  # this gives two star systems on the same (x,y) with p = {'maxX':12,'maxY':12,'minZ':-12,'maxZ':12}
    #	p = {'maxX':12,'maxY':12,'minZ':-12,'maxZ':12,'stellarDensity':0.004,'filename':"sampleMap.svg"}
    # Rael map parameters
    #	p = {'maxX':40,'maxY':40,'minZ':-10,'maxZ':10,'stellarDensity':0.004,'filename':"JordMap.svg"
    #		,'datafile':"sampleSystemData.txt",'scale':1.0,'printZ':True}
    # Random map parameters
    p = {'maxX': 94, 'maxY': 20, 'minZ': -12, 'maxZ': 12, 'stellarDensity': 0.0015, 'filename': "sampleMap.svg"
        , 'datafile': "sampleSystemData.txt", 'scale': 1.0, 'printZ': True}
    # Big SF Map
    #	p = {'maxX':90,'maxY':100,'minZ':-12,'maxZ':12,'stellarDensity':0.004,'filename':"ExtendedFrontierMap-sathar.svg"
    #		,'datafile':"sampleSystemData.txt",'scale':1.5,'printZ':False}

    # parse command-line options for size of map, 2D or 3D, grid type, distance threshold and whatever else I think to add

    # generate list of star system data
    from loadData import loadData

    loadFile = "YaziraSectorData.txt"
    if loadFile:  # read the data from the specified file
        starList = []
        jumpList = []
        loadData(loadFile, p, starList, jumpList)
    else:  # generate the data randomly
        starList = createSystems(p)
        jumpList = findJumps(starList)

    print("there are", len(starList), "systems on the map")

    # check for overlapping systems and flag
    multipleList = findOverlaps(starList)

    defDict = {}  # dictionary of gradient definitions for star symbols in SVG file
    # generate symbols for each system
    symbolList = createMapSymbols(p, starList, multipleList, defDict)

    # generate stellar distance data
    connectionList = findConnections(starList, jumpList)

    # draw map
    createMap(p, defDict, symbolList, connectionList, starList)

    # write out the star system data
    from writeData import writeSystemData, writeConnectionData

    writeSystemData(p, starList)
    writeConnectionData(p, jumpList)
