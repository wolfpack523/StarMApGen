class JumpLink:
    STATUS_NORMAL = "normal"
    STATUS_CAUTION = "caution"
    STATUS_DANGEROUS = "dangerous"
    STATUS_BLOCKED = "blocked"
    STATUS_LOST = "lost"

    VALID_STATUSES = {
        STATUS_NORMAL,
        STATUS_CAUTION,
        STATUS_DANGEROUS,
        STATUS_BLOCKED,
        STATUS_LOST
    }

    def __init__(
            self,
            startName,
            endName,
            status=STATUS_NORMAL,
    ):
        self.startName = startName
        self.endName = endName
        self.status = status

    def contains(self, systemName):
        return (
                self.startName == systemName
                or self.endName == systemName
        )

    def getOtherSystemName(self, systemName):
        if self.startName == systemName:
            return self.endName

        if self.endName == systemName:
            return self.startName

        return None

    def renameSystem(self, oldName, newName):
        if self.startName == oldName:
            self.startName = newName

        if self.endName == oldName:
            self.endName = newName
