import wx

from JumpLink import JumpLink
from JumpLinkDialog import (
    JumpLinkDialog,
    JUMP_STATUS_OPTIONS,
)


JUMP_STATUS_LABELS = dict(
    JUMP_STATUS_OPTIONS
)


class JumpLinkEditorPanel(wx.Panel):
    """Editor for jump links of one star system."""

    def __init__(
            self,
            parent,
            controller,
    ):
        super().__init__(parent)

        self.controller = controller

        self.systemName = None
        self.displayedJumpLinks = []

        self.createControls()

    @property
    def starList(self):
        return self.controller.starList

    @property
    def jumpList(self):
        return self.controller.jumpList

    @jumpList.setter
    def jumpList(
            self,
            value,
    ):
        self.controller.jumpList = value

    def saveAndRedrawCurrentMap(self):
        self.controller.saveAndRedrawCurrentMap()

    def SetStatusText(
            self,
            text,
    ):
        self.controller.SetStatusText(
            text
        )

    def createControls(self):
        panel_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        panel_sizer.Add(
            wx.StaticText(
                self,
                label="Jump Links:",
            ),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            5,
            )

        jump_hint = wx.StaticText(
            self,
            label=(
                "Add, edit, or remove jump links and assign "
                "a route status to each connection."
            ),
        )

        jump_hint.Wrap(
            330
        )

        panel_sizer.Add(
            jump_hint,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
            )

        self.jumpListControl = wx.ListCtrl(
            self,
            size=(-1, 120),
            style=(
                    wx.LC_REPORT
                    | wx.LC_SINGLE_SEL
                    | wx.BORDER_SUNKEN
            ),
        )

        self.jumpListControl.InsertColumn(
            0,
            "System",
            width=190,
        )

        self.jumpListControl.InsertColumn(
            1,
            "Status",
            width=110,
        )

        self.jumpListControl.Bind(
            wx.EVT_LIST_ITEM_SELECTED,
            self.onJumpSelectionChanged,
        )

        self.jumpListControl.Bind(
            wx.EVT_LIST_ITEM_DESELECTED,
            self.onJumpSelectionChanged,
        )

        self.jumpListControl.Bind(
            wx.EVT_LIST_ITEM_ACTIVATED,
            self.editJumpLink,
        )

        self.jumpListControl.Disable()

        panel_sizer.Add(
            self.jumpListControl,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
            )

        button_sizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        self.addJumpButton = wx.Button(
            self,
            label="Add Link",
        )

        self.addJumpButton.Bind(
            wx.EVT_BUTTON,
            self.addJumpLink,
        )

        self.addJumpButton.Disable()

        button_sizer.Add(
            self.addJumpButton,
            0,
            wx.RIGHT,
            5,
        )

        self.editJumpButton = wx.Button(
            self,
            label="Edit Link",
        )

        self.editJumpButton.Bind(
            wx.EVT_BUTTON,
            self.editJumpLink,
        )

        self.editJumpButton.Disable()

        button_sizer.Add(
            self.editJumpButton,
            0,
            wx.RIGHT,
            5,
        )

        self.removeJumpButton = wx.Button(
            self,
            label="Remove Link",
        )

        self.removeJumpButton.Bind(
            wx.EVT_BUTTON,
            self.removeJumpLink,
        )

        self.removeJumpButton.Disable()

        button_sizer.Add(
            self.removeJumpButton,
            0,
        )

        panel_sizer.Add(
            button_sizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.ALIGN_RIGHT,
            5,
            )

        self.SetSizer(
            panel_sizer
        )

    def setSystem(
            self,
            system_name,
    ):
        """Display jump links for one system."""

        self.systemName = system_name
        self.refreshJumpEditor()

    def clear(self):
        self.systemName = None
        self.displayedJumpLinks = []

        self.jumpListControl.DeleteAllItems()
        self.jumpListControl.Disable()

        self.addJumpButton.Disable()
        self.editJumpButton.Disable()
        self.removeJumpButton.Disable()

    def refreshJumpEditor(self):
        self.displayedJumpLinks = []
        self.jumpListControl.DeleteAllItems()

        if self.systemName is None:
            self.jumpListControl.Disable()
            self.updateJumpButtons()
            return

        displayed_links = []

        for jump in self.jumpList:
            if not jump.contains(
                    self.systemName
            ):
                continue

            other_name = (
                jump.getOtherSystemName(
                    self.systemName
                )
            )

            if other_name is None:
                continue

            displayed_links.append(
                (
                    other_name,
                    jump,
                )
            )

        displayed_links.sort(
            key=lambda item:
            item[0].casefold()
        )

        for other_name, jump in displayed_links:
            row = (
                self.jumpListControl
                .InsertItem(
                    self.jumpListControl
                    .GetItemCount(),
                    other_name,
                    )
            )

            self.jumpListControl.SetItem(
                row,
                1,
                JUMP_STATUS_LABELS.get(
                    jump.status,
                    jump.status,
                ),
            )

            self.displayedJumpLinks.append(
                jump
            )

        self.jumpListControl.Enable()

        self.updateJumpButtons()

    def onJumpSelectionChanged(
            self,
            event,
    ):
        self.updateJumpButtons()
        event.Skip()

    def updateJumpButtons(self):
        can_edit = (
                self.systemName is not None
                and self.getSelectedJumpLink()
                is not None
        )

        can_add = (
                self.systemName is not None
                and bool(
            self.getAvailableJumpTargets()
        )
        )

        self.addJumpButton.Enable(
            can_add
        )

        self.editJumpButton.Enable(
            can_edit
        )

        self.removeJumpButton.Enable(
            can_edit
        )

    def getSelectedJumpLink(self):
        selected_row = (
            self.jumpListControl
            .GetFirstSelected()
        )

        if (
                selected_row == -1
                or not 0 <= selected_row
                       < len(
            self.displayedJumpLinks
        )
        ):
            return None

        return (
            self.displayedJumpLinks[
                selected_row
            ]
        )

    def getAvailableJumpTargets(
            self,
            current_target=None,
    ):
        if self.systemName is None:
            return []

        connected_names = {
            jump.getOtherSystemName(
                self.systemName
            )
            for jump in self.jumpList
            if jump.contains(
                self.systemName
            )
        }

        return sorted(
            [
                system.name
                for system in self.starList
                if (
                    system.name
                    != self.systemName
                    and (
                            system.name
                            == current_target
                            or system.name
                            not in connected_names
                    )
            )
            ],
            key=str.casefold,
        )

    def addJumpLink(
            self,
            event,
    ):
        if self.systemName is None:
            return

        target_names = (
            self.getAvailableJumpTargets()
        )

        if not target_names:
            wx.MessageBox(
                "There are no unconnected star systems.",
                "Add Jump Link",
                wx.OK
                | wx.ICON_INFORMATION,
                )
            return

        dialog = JumpLinkDialog(
            self,
            target_names,
            title="Add Jump Link",
        )

        try:
            if (
                    dialog.ShowModal()
                    != wx.ID_OK
            ):
                return

            target_name = (
                dialog.getTargetName()
            )

            status = (
                dialog.getStatus()
            )

        finally:
            dialog.Destroy()

        self.jumpList.append(
            JumpLink(
                self.systemName,
                target_name,
                status,
            )
        )

        self.saveAndRedrawCurrentMap()
        self.refreshJumpEditor()

        self.SetStatusText(
            f'Jump link to "{target_name}" '
            "was added."
        )

    def editJumpLink(
            self,
            event,
    ):
        jump = (
            self.getSelectedJumpLink()
        )

        if (
                self.systemName is None
                or jump is None
        ):
            return

        current_target = (
            jump.getOtherSystemName(
                self.systemName
            )
        )

        target_names = (
            self.getAvailableJumpTargets(
                current_target
            )
        )

        dialog = JumpLinkDialog(
            self,
            target_names,
            target_name=current_target,
            status=jump.status,
            title="Edit Jump Link",
        )

        try:
            if (
                    dialog.ShowModal()
                    != wx.ID_OK
            ):
                return

            target_name = (
                dialog.getTargetName()
            )

            status = (
                dialog.getStatus()
            )

        finally:
            dialog.Destroy()

        jump.startName = (
            self.systemName
        )

        jump.endName = target_name
        jump.status = status

        self.saveAndRedrawCurrentMap()
        self.refreshJumpEditor()

        self.SetStatusText(
            f'Jump link to "{target_name}" '
            "was updated."
        )

    def removeJumpLink(
            self,
            event,
    ):
        jump = (
            self.getSelectedJumpLink()
        )

        if (
                self.systemName is None
                or jump is None
        ):
            return

        target_name = (
            jump.getOtherSystemName(
                self.systemName
            )
        )

        result = wx.MessageBox(
            f'Remove the jump link to '
            f'"{target_name}"?',
            "Remove Jump Link",
            wx.YES_NO
            | wx.NO_DEFAULT
            | wx.ICON_QUESTION,
            )

        if result != wx.YES:
            return

        self.jumpList.remove(
            jump
        )

        self.saveAndRedrawCurrentMap()
        self.refreshJumpEditor()

        self.SetStatusText(
            f'Jump link to "{target_name}" '
            "was removed."
        )