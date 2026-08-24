from svgHelpers import (
    escape_svg_attribute,
)

P2MM = 0.26458333333

def write_nebulae(
        params,
        file,
        nebula_list,
):
    """Draw all nebulae below the map grid."""

    if not nebula_list:
        return

    file.write(
        '<g id="nebulae">\n'
    )

    for index, nebula in enumerate(
            nebula_list
    ):
        write_nebula(
            params,
            file,
            nebula,
            index,
        )

    file.write(
        "</g>\n"
    )


def write_nebula(
        params,
        file,
        nebula,
        index,
):
    """Draw one smooth nebula boundary."""

    if len(nebula.points) < 3:
        return

    points = get_nebula_svg_points(
        params,
        nebula,
    )

    path_data = create_smooth_closed_path(
        points,
        tension=get_nebula_tension(
            nebula.style
        ),
    )

    file.write(
        f'<g id="nebula-{index}" '
        f'data-nebula-name="{escape_svg_attribute(nebula.name)}" '
        f'data-nebula-style="{nebula.style}">\n'
    )

    if nebula.style == "outline":
        file.write(
            '<path '
            f'd="{path_data}" '
            'fill="none" '
            f'stroke="{nebula.color}" '
            f'stroke-opacity="{nebula.opacity:f}" '
            f'stroke-width="{6 * P2MM:f}" '
            'stroke-linejoin="round" '
            'stroke-linecap="round" '
            '/>\n'
        )

    elif nebula.style == "haze":
        file.write(
            '<path '
            f'd="{path_data}" '
            f'fill="{nebula.color}" '
            f'fill-opacity="{nebula.opacity * 0.55:f}" '
            f'stroke="{nebula.color}" '
            f'stroke-opacity="{nebula.opacity * 0.35:f}" '
            f'stroke-width="{18 * P2MM:f}" '
            'stroke-linejoin="round" '
            'stroke-linecap="round" '
            '/>\n'
        )

    else:
        file.write(
            '<path '
            f'd="{path_data}" '
            f'fill="{nebula.color}" '
            f'fill-opacity="{nebula.opacity:f}" '
            'stroke="none" '
            '/>\n'
        )

    file.write(
        "</g>\n"
    )

def get_nebula_svg_points(
        params,
        nebula,
):
    min_x = params.get(
        "minX",
        1,
    )

    min_y = params.get(
        "minY",
        1,
    )

    svg_points = []

    for x, y in nebula.points:
        local_x = (
                x
                - min_x
                + 1
        )

        local_y = (
                y
                - min_y
                + 1
        )

        svg_x = (
                local_x
                * 150
                * P2MM
        )

        svg_y = (
                local_y
                * 150
                * P2MM
        )

        svg_points.append(
            (
                svg_x,
                svg_y,
            )
        )

    return svg_points


def create_smooth_closed_path(
        points,
        tension=1.0,
):
    if len(points) < 3:
        return ""

    commands = []

    first_point = points[0]

    commands.append(
        f"M {first_point[0]:f},{first_point[1]:f}"
    )

    point_count = len(points)

    for index in range(point_count):
        previous_point = points[
            (index - 1) % point_count
            ]

        current_point = points[
            index
        ]

        next_point = points[
            (index + 1) % point_count
            ]

        next_next_point = points[
            (index + 2) % point_count
            ]

        control_point1 = (
            current_point[0]
            + (
                    next_point[0]
                    - previous_point[0]
            )
            * tension
            / 6.0,
            current_point[1]
            + (
                    next_point[1]
                    - previous_point[1]
            )
            * tension
            / 6.0,
        )

        control_point2 = (
            next_point[0]
            - (
                    next_next_point[0]
                    - current_point[0]
            )
            * tension
            / 6.0,
            next_point[1]
            - (
                    next_next_point[1]
                    - current_point[1]
            )
            * tension
            / 6.0,
        )

        commands.append(
            "C "
            f"{control_point1[0]:f},"
            f"{control_point1[1]:f} "
            f"{control_point2[0]:f},"
            f"{control_point2[1]:f} "
            f"{next_point[0]:f},"
            f"{next_point[1]:f}"
        )

    commands.append("Z")

    return " ".join(commands)


def get_nebula_tension(style):
    if style == "outline":
        return 0.65

    if style == "haze":
        return 1.5

    return 1.0
