from JumpLink import JumpLink


def writeSystemData(params, systemList):
    """Write all star systems to the configured DAT file."""

    with open(
            params["datafile"],
            "w",
            encoding="utf-8",
    ) as file:
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
