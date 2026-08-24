#!/usr/bin/env python
from StarSystem import StarSystem

from jumpRendering import (
    draw_connections,
    find_connections,
    find_jumps,
)
from nebulaRendering import (
    write_nebulae,
)
from svgHelpers import (
    write_axis_labels,
    write_defs,
    write_map_header,
    write_names,
    write_symbols,
)
from systemRendering import (
    create_map_symbols,
    find_overlaps,
)

p2mm = 0.26458333333  # /25.4/96


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

    min_x = params.get(
        "minX",
        1,
    )

    min_y = params.get(
        "minY",
        1,
    )

    map_width = (
            params["maxX"]
            - min_x
            + 1
    )

    map_height = (
            params["maxY"]
            - min_y
            + 1
    )

    width = (
            (map_width + 1)
            * 150
            * p2mm
    )

    height = (
            (map_height + 1)
            * 150
            * p2mm
    )

    with open(
            params["filename"],
            "w",
            encoding="utf-8",
    ) as file:
        write_map_header(
            file,
            width,
            height,
        )

        write_defs(
            file,
            defDict,
        )

        _write_background(
            file,
            width,
            height,
        )

        _write_grid(
            file,
            map_width,
            map_height,
        )

        write_axis_labels(
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

        file.write(
            "</g>\n"
        )

        file.write(
            '<g id="stars" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Stars">\n'
        )

        write_symbols(
            file,
            symbolList,
        )

        file.write(
            "</g>\n"
        )

        file.write(
            '<g id="names" '
            'inkscape:groupmode="layer" '
            'inkscape:label="Names">\n'
        )

        write_names(
            params,
            file,
            starList,
        )

        file.write(
            "</g>\n"
        )

        file.write(
            "</svg>"
        )


def _write_background(
        file,
        width,
        height,
):
    """Write the map background layer."""

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

    file.write(
        "</g>\n"
    )

def _write_grid(
        file,
        map_width,
        map_height,
):
    """Write the map coordinate grid."""

    file.write(
        '<g id="grid" '
        'inkscape:groupmode="layer" '
        'inkscape:label="Grid">\n'
    )

    x_min = 75
    y_min = 75

    x_max = (
            map_width
            * 150
            + 75
    )

    y_max = (
            map_height
            * 150
            + 75
    )

    for index in range(
            map_width + 1
    ):
        x = (
                index
                * 150
                + 75
        )

        file.write(
            '<line '
            f'x1="{x * p2mm:f}" '
            f'y1="{y_min * p2mm:f}" '
            f'x2="{x * p2mm:f}" '
            f'y2="{y_max * p2mm:f}" '
            'style="stroke:rgb(100,100,100); '
            f'stroke-width:{3 * p2mm:f}" />\n'
        )

    for index in range(
            map_height + 1
    ):
        y = (
                index
                * 150
                + 75
        )

        file.write(
            '<line '
            f'x1="{x_min * p2mm:f}" '
            f'y1="{y * p2mm:f}" '
            f'x2="{x_max * p2mm:f}" '
            f'y2="{y * p2mm:f}" '
            'style="stroke:rgb(100,100,100); '
            f'stroke-width:{3 * p2mm:f}" />\n'
        )

    file.write(
        "</g>\n"
    )

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
    multipleList = find_overlaps(starList)

    defDict = {}  # dictionary of gradient definitions for star symbols in SVG file
    # generate symbols for each system
    symbolList = create_map_symbols(p, starList, multipleList, defDict)

    # generate stellar distance data
    connectionList = find_connections(starList, jumpList)

    # draw map
    createMap(p, defDict, symbolList, connectionList, starList)

    # write out the star system data
    from writeData import writeSystemData, writeConnectionData

    writeSystemData(p, starList)
    writeConnectionData(p, jumpList)

