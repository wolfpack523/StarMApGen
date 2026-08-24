#!/usr/bin/env python
from StarSystem import StarSystem
from starRendering import (
    create_symbol,
    get_star_offset_list,
    get_tweak_offset,
    sort_spec_type_for_display,
)

p2mm = 0.26458333333  # /25.4/96

from jumpRendering import (
    draw_connections,
    find_connections,
    find_jumps,
)

from nebulaRendering import (
    write_nebulae,
)


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
            starOffset = get_star_offset_list(
                system.nStars
            )

            tweakOffset = get_tweak_offset(
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

        tooltipText = createSystemTooltipText(
            system
        )

        data = (
                '<g '
                'class="star-system" '
                f'data-system-name="{escapeSvgAttribute(system.name)}" '
                f'data-tooltip="{escapeSvgAttribute(tooltipText)}" '
                'transform="translate(%f,%f)">'
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
            key=sort_spec_type_for_display,
        )

        for index, star in enumerate(stars):
            data += create_symbol(
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


def writeMapHeader(f, w, h):
    """Write a clean, standards-compliant SVG header."""

    f.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
    )

    f.write(
        '<svg '
        'xmlns="http://www.w3.org/2000/svg" '
        'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        'version="1.1" '
        f'viewBox="0 0 {w:.6f} {h:.6f}" '
        f'width="{w:.6f}" '
        f'height="{h:.6f}" '
        'preserveAspectRatio="xMidYMid meet">'
        '\n'
    )






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

        writeAxisLabels(
            params,
            file,
        )

        write_nebulae(
            params,
            file,
            nebulaList,
        )

        file.write(
            '<g id="jumps" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Jumps">\n'
        )

        draw_connections(
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
        jumpList = find_jumps(starList)

    print("there are", len(starList), "systems on the map")

    # check for overlapping systems and flag
    multipleList = findOverlaps(starList)

    defDict = {}  # dictionary of gradient definitions for star symbols in SVG file
    # generate symbols for each system
    symbolList = createMapSymbols(p, starList, multipleList, defDict)

    # generate stellar distance data
    connectionList = find_connections(starList, jumpList)

    # draw map
    createMap(p, defDict, symbolList, connectionList, starList)

    # write out the star system data
    from writeData import writeSystemData, writeConnectionData

    writeSystemData(p, starList)
    writeConnectionData(p, jumpList)

def writeAxisLabels(
        params,
        file,
):
    """Draw X and Y coordinate labels along the map edges."""

    minX = params.get(
        "minX",
        1,
    )

    maxX = params.get(
        "maxX",
        minX,
    )

    minY = params.get(
        "minY",
        1,
    )

    maxY = params.get(
        "maxY",
        minY,
    )

    fontSize = 24 * p2mm

    file.write(
        '<g id="axis-labels">\n'
    )

    # X axis labels at the top.
    for x in range(
            minX,
            maxX + 1,
    ):
        localX = (
                x
                - minX
                + 1
        )

        svgX = (
                localX
                * 150
                * p2mm
        )

        svgY = (
                35
                * p2mm
        )

        file.write(
            '<text '
            f'x="{svgX:f}" '
            f'y="{svgY:f}" '
            f'font-size="{fontSize:f}" '
            'font-family="Arial,Helvetica,sans-serif" '
            'fill="#b0b0b0" '
            'text-anchor="middle">'
            f'{x}'
            '</text>\n'
        )

    # Y axis labels on the left.
    for y in range(
            minY,
            maxY + 1,
    ):
        localY = (
                y
                - minY
                + 1
        )

        svgX = (
                35
                * p2mm
        )

        svgY = (
                localY
                * 150
                * p2mm
        )

        file.write(
            '<text '
            f'x="{svgX:f}" '
            f'y="{svgY:f}" '
            f'font-size="{fontSize:f}" '
            'font-family="Arial,Helvetica,sans-serif" '
            'fill="#b0b0b0" '
            'text-anchor="middle" '
            'dominant-baseline="middle">'
            f'{y}'
            '</text>\n'
        )

    file.write(
        "</g>\n"
    )

def createSystemTooltipText(system):
    """Create the tooltip text stored on a star system SVG group."""

    lines = [
        system.name,
    ]

    if system.faction:
        lines.append(
            f"Faction: {system.faction}"
        )

    lines.append(
        f"Stars: {', '.join(system.stars)}"
    )

    if system.planets:
        lines.append("")

        for planet in system.planets:
            lines.append(
                f"{planet.name} — "
                f"{planet.getTypeLabel()} — "
                f"{planet.classification}"
            )

    return "\n".join(lines)