from domain.JumpLink import JumpLink

def writeSystemData(params, systemList):
    """Write the map bounds and all star systems."""

    minX = params.get("minX", 1)
    minY = params.get("minY", 1)
    minZ = params.get("minZ", 0)

    maxX = params.get("maxX", minX)
    maxY = params.get("maxY", minY)
    maxZ = params.get("maxZ", minZ)

    with open(
            params["datafile"],
            "w",
            encoding="utf-8",
    ) as file:
        file.write(
            f"Map Minimum: ({minX},{minY},{minZ})\n"
        )

        file.write(
            f"Map Maximum: ({maxX},{maxY},{maxZ})\n\n"
        )

        for system in systemList:
            file.write(
                f"Name: {system.name}\n"
            )

            file.write(
                "Coordinates: "
                f"({system.x},{system.y},{system.z})\n"
            )

            file.write(
                f"Number of Stars: {len(system.stars)}\n"
            )

            file.write(
                "Spectral Types: "
                + ", ".join(system.stars)
                + "\n\n"
            )


def writeConnectionData(params, jumpList):
    """Append all jump links and their status to the DAT file."""

    with open(
            params["datafile"],
            "a",
            encoding="utf-8",
    ) as file:
        for jump in jumpList:
            status = jump.status

            if status not in JumpLink.VALID_STATUSES:
                status = JumpLink.STATUS_NORMAL

            file.write(
                f'Link: "{jump.startName}" '
                f'"{jump.endName}" '
                f'"{status}"\n'
            )

        file.write("\n")

def writeNebulaData(params, nebulaList):
    """Append all nebulae to the DAT file."""

    with open(
            params["datafile"],
            "a",
            encoding="utf-8",
    ) as file:
        for nebula in nebulaList:
            file.write(
                f"Nebula: {nebula.name}\n"
            )

            file.write(
                f"Style: {nebula.style}\n"
            )

            file.write(
                f"Color: {nebula.color}\n"
            )

            file.write(
                f"Opacity: {nebula.opacity:.2f}\n"
            )

            points = ", ".join(
                f"({x},{y})"
                for x, y in nebula.points
            )

            file.write(
                f"Points: {points}\n\n"
            )

def writePlanetData(
        params,
        systemList,
):
    """Append all planets to the DAT file."""

    with open(
            params["datafile"],
            "a",
            encoding="utf-8",
    ) as file:
        for system in systemList:
            for planet in system.planets:
                file.write(
                    f'Planet: "{system.name}" '
                    f'"{planet.name}" '
                    f'"{planet.planetType}" '
                    f'"{planet.classification}"\n'
                )

        file.write("\n")

def writeFactionData(
        params,
        systemList,
):
    """Append system factions to the DAT file."""

    with open(
            params["datafile"],
            "a",
            encoding="utf-8",
    ) as file:
        for system in systemList:
            if not system.faction:
                continue

            file.write(
                f'Faction: "{system.name}" '
                f'"{system.faction}"\n'
            )

        file.write("\n")