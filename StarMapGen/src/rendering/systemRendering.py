from rendering.starRendering import (
    create_symbol,
    get_star_offset_list,
    get_tweak_offset,
    sort_spec_type_for_display,
)
from rendering.svgHelpers import (
    escape_svg_attribute,
)
from rendering.svgHelpers import P2MM


from collections import Counter


def find_overlaps(
        system_list,
):
    position_counts = Counter(
        system.mapPos
        for system in system_list
    )

    multiple_positions = [
        position
        for position, count
        in position_counts.items()
        if count > 1
    ]

    for position in multiple_positions:
        print(
            "there are",
            position_counts[position],
            "systems at",
            position,
        )

    return multiple_positions


def create_system_tooltip_text(
        system,
):
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

    return "\n".join(
        lines
    )


def create_map_symbols(
        p,
        system_list,
        m_list,
        def_dict,
):
    symbol_list = []
    dup_list = {}

    system_offsets = [
        (0, 0),
        (-30, 30),
        (30, -30),
        (-30, -30),
        (30, 30),
    ]

    min_x = p.get("minX", 1)
    min_y = p.get("minY", 1)

    for system in system_list:
        tweak_offset = (0, 0)
        dup_count = 0

        # Handle multiple star systems at the same absolute
        # X/Y coordinate.
        if system.mapPos in m_list:
            if system.mapPos in dup_list:
                dup_count = (
                        dup_list[system.mapPos] + 1
                )
            else:
                dup_count = 1

            dup_list[system.mapPos] = dup_count

        star_offset = [(0, 0)]

        if system.nStars > 1:
            star_offset = get_star_offset_list(
                system.nStars
            )

            tweak_offset = get_tweak_offset(
                system.stars
            )

        # Translate absolute map coordinates into coordinates
        # relative to the current map minimum.
        local_x = (
                system.mapPos[0]
                - min_x
                + 1
        )

        local_y = (
                system.mapPos[1]
                - min_y
                + 1
        )

        x_pos = (
                local_x * 150
                + system_offsets[dup_count][0]
                + tweak_offset[0]
        )

        y_pos = (
                local_y * 150
                + system_offsets[dup_count][1]
                + tweak_offset[1]
        )

        tooltip_text = create_system_tooltip_text(
            system
        )

        data = (
                '<g '
                'class="star-system" '
                f'data-system-name="{escape_svg_attribute(system.name)}" '
                f'data-tooltip="{escape_svg_attribute(tooltip_text)}" '
                'transform="translate(%f,%f)">'
                % (
                    x_pos * P2MM,
                    y_pos * P2MM,
                )
        )

        # Keep track of the system centre for jump lines and names.
        system.drawnPos = (
            x_pos - tweak_offset[0],
            y_pos - tweak_offset[1],
        )

        stars = sorted(
            system.stars,
            key=sort_spec_type_for_display,
        )

        for index, star in enumerate(stars):
            data += create_symbol(
                p,
                star,
                star_offset[index],
                def_dict,
            )

        if p["printZ"]:
            height = 30

            data += (
                    '<text x="%f" y="%f" font-size="%d" '
                    'font-family="Arial,Helvetica,sans-serif" '
                    'fill="white">'
                    % (
                        20 * p["scale"] * P2MM,
                        height * p["scale"] * P2MM,
                        height * P2MM,
                    )
            )

            if system.z > 0:
                data += "+"

            data += "%d</text>" % system.z

        data += "</g>"
        symbol_list.append(data)

    return symbol_list
