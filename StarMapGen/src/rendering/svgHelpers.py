P2MM = 0.26458333333

def write_defs(
        file,
        definitions,
):
    file.write(
        " <defs>\n"
    )

    for definition in definitions.values():
        file.write(
            definition
        )

    file.write(
        " </defs>\n"
    )


def write_symbols(
        file,
        symbols,
):
    for symbol in symbols:
        file.write(
            symbol
        )


def write_map_header(
        file,
        width,
        height,
):
    """Write a clean, standards-compliant SVG header."""

    file.write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
    )

    file.write(
        '<svg '
        'xmlns="http://www.w3.org/2000/svg" '
        'xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
        'version="1.1" '
        f'viewBox="0 0 {width:.6f} {height:.6f}" '
        f'width="{width:.6f}" '
        f'height="{height:.6f}" '
        'preserveAspectRatio="xMidYMid meet">'
        '\n'
    )


def write_names(
        params,
        file,
        system_list,
):
    """Draw the names of all star systems."""

    offset = (
            params["scale"]
            * 25
    )

    for system in system_list:
        data = (
            '<g><text '
            f'x="{(system.drawnPos[0] + offset) * P2MM:f}" '
            f'y="{(system.drawnPos[1] - offset) * P2MM:f}" '
            f'font-size="{50 * params["scale"] * P2MM:f}" '
            'font-family="Arial, Helvetica, sans-serif" '
            'fill="white">'
            f'{system.name}'
            '</text></g>\n'
        )

        file.write(
            data
        )


def escape_svg_attribute(
        value,
):
    """Escape text used inside an SVG attribute."""

    return (
        str(value)
        .replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def write_axis_labels(
        params,
        file,
):
    """Draw X and Y coordinate labels along the map edges."""

    min_x = params.get(
        "minX",
        1,
    )

    max_x = params.get(
        "maxX",
        min_x,
    )

    min_y = params.get(
        "minY",
        1,
    )

    max_y = params.get(
        "maxY",
        min_y,
    )

    font_size = (
            24
            * P2MM
    )

    file.write(
        '<g id="axis-labels">\n'
    )

    for x in range(
            min_x,
            max_x + 1,
    ):
        local_x = (
                x
                - min_x
                + 1
        )

        svg_x = (
                local_x
                * 150
                * P2MM
        )

        svg_y = (
                35
                * P2MM
        )

        file.write(
            '<text '
            f'x="{svg_x:f}" '
            f'y="{svg_y:f}" '
            f'font-size="{font_size:f}" '
            'font-family="Arial,Helvetica,sans-serif" '
            'fill="#b0b0b0" '
            'text-anchor="middle">'
            f'{x}'
            '</text>\n'
        )

    for y in range(
            min_y,
            max_y + 1,
    ):
        local_y = (
                y
                - min_y
                + 1
        )

        svg_x = (
                35
                * P2MM
        )

        svg_y = (
                local_y
                * 150
                * P2MM
        )

        file.write(
            '<text '
            f'x="{svg_x:f}" '
            f'y="{svg_y:f}" '
            f'font-size="{font_size:f}" '
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