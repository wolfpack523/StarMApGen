import math

from domain.JumpLink import JumpLink
from rendering.svgHelpers import P2MM


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

def find_connections(
        system_list,
        jump_list,
):
    """Create drawable connection data from JumpLink objects."""

    connection_list = []

    systems_by_name = {
        system.name: system
        for system in system_list
    }

    for jump in jump_list:
        if isinstance(jump, JumpLink):
            start_name = jump.startName
            end_name = jump.endName
            status = jump.status
        else:
            try:
                start_name = jump[0]
                end_name = jump[1]
            except (IndexError, TypeError):
                print(
                    f"Ignoring invalid jump link: {jump}"
                )
                continue

            status = JumpLink.STATUS_NORMAL

        start_system = systems_by_name.get(
            start_name
        )

        end_system = systems_by_name.get(
            end_name
        )

        if (
                start_system is None
                or end_system is None
        ):
            print(
                f'Ignoring jump link "{start_name}" -> '
                f'"{end_name}" because a system is missing.'
            )
            continue

        if start_system is end_system:
            print(
                f'Ignoring self-link for "{start_name}".'
            )
            continue

        delta_x = (
                start_system.x
                - end_system.x
        )

        delta_y = (
                start_system.y
                - end_system.y
        )

        delta_z = (
                start_system.z
                - end_system.z
        )

        distance = int(
            math.sqrt(
                delta_x * delta_x
                + delta_y * delta_y
                + delta_z * delta_z
            )
            + 0.5
        )

        connection_list.append(
            (
                start_system.drawnPos,
                end_system.drawnPos,
                distance,
                status,
            )
        )

    return connection_list


def find_jumps(
        system_list,
):
    """Generate normal jump links between nearby habitable systems."""

    jump_list = []

    habitable_systems = [
        system
        for system in system_list
        if system.hasHabitable()
    ]

    for first_index in range(
            len(habitable_systems)
    ):
        for second_index in range(
                first_index + 1,
                len(habitable_systems),
        ):
            first_system = (
                habitable_systems[
                    first_index
                ]
            )

            second_system = (
                habitable_systems[
                    second_index
                ]
            )

            delta_x = (
                    first_system.x
                    - second_system.x
            )

            delta_y = (
                    first_system.y
                    - second_system.y
            )

            delta_z = (
                    first_system.z
                    - second_system.z
            )

            distance = int(
                math.sqrt(
                    delta_x * delta_x
                    + delta_y * delta_y
                    + delta_z * delta_z
                )
                + 0.5
            )

            if distance < 15:
                jump_list.append(
                    JumpLink(
                        first_system.name,
                        second_system.name,
                        JumpLink.STATUS_NORMAL,
                    )
                )

    return jump_list

def draw_connections(params, file, connection_list):
    """Draw jump links using their configured route status."""

    for connection in connection_list:
        start_position = connection[0]
        end_position = connection[1]
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

        stroke_width = (
                style["strokeWidth"]
                * P2MM
        )

        style_parts = [
            f"stroke:{color}",
            f"stroke-width:{stroke_width:f}",
            "fill:none",
        ]

        dash = style["dash"]

        if dash is not None:
            dash_array = ",".join(
                f"{value * P2MM:f}"
                for value in dash
            )

            style_parts.append(
                f"stroke-dasharray:{dash_array}"
            )

        line_style = "; ".join(style_parts)

        data = (
            f'<g data-jump-status="{status}">'
            f'<line style="{line_style}"'
        )

        data += (
                ' x1="%f" y1="%f" x2="%f" y2="%f" />\n'
                % (
                    start_position[0] * P2MM,
                    start_position[1] * P2MM,
                    end_position[0] * P2MM,
                    end_position[1] * P2MM,
                )
        )

        offset = (-45.0, -45.0)
        x_scale = 0.0
        y_scale = 0.0
        slope = 0.0
        angle = 0.0

        x1 = float(start_position[0])
        x2 = float(end_position[0])
        y1 = float(start_position[1])
        y2 = float(end_position[1])

        if x1 != x2:
            slope = (y1 - y2) / (x2 - x1)
            angle = math.atan(-slope) * 180 / math.acos(-1.0)

            x_scale = math.sin(
                math.atan(slope) * 2
            )

            y_scale = math.sin(
                math.atan(slope) * 2
            )

            if math.fabs(angle) >= 45.0:
                x_scale = -x_scale

            if slope < 0:
                x_scale = -x_scale
        else:
            x_scale = -0.2
            y_scale = 0

        if slope == 0:
            y_scale /= 2
        elif math.fabs(angle) < 10:
            y_scale *= 0.8

        x_middle = (
                          start_position[0] + end_position[0]
                  ) / 2 + x_scale * offset[0]

        y_middle = (
                          start_position[1] + end_position[1]
                  ) / 2 + y_scale * offset[1]

        data += (
                '<text x="%f" y="%f" font-size="%f" '
                'font-family="Arial,Helvetica,sans-serif" '
                'fill="%s">'
                % (
                    x_middle * P2MM,
                    y_middle * P2MM,
                    40 * params["scale"] * P2MM,
                    color,
                )
        )

        data += (
            f"{distance}</text></g>\n"
        )

        file.write(data)
