import wx

from JumpLink import JumpLink


JUMP_STATUS_OPTIONS = [
    (
        JumpLink.STATUS_NORMAL,
        "Normal",
    ),
    (
        JumpLink.STATUS_CAUTION,
        "Caution",
    ),
    (
        JumpLink.STATUS_DANGEROUS,
        "Dangerous",
    ),
    (
        JumpLink.STATUS_BLOCKED,
        "Blocked",
    ),
    (
        JumpLink.STATUS_LOST,
        "Lost",
    ),
]


class JumpLinkDialog(wx.Dialog):
    """Dialog for creating or editing a jump link."""

    def __init__(
            self,
            parent,
            target_names,
            target_name=None,
            status=JumpLink.STATUS_NORMAL,
            title="Jump Link",
    ):
        super().__init__(
            parent,
            title=title,
        )

        main_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        form_sizer = wx.FlexGridSizer(
            cols=2,
            vgap=8,
            hgap=8,
        )

        form_sizer.AddGrowableCol(
            1,
            1,
        )

        form_sizer.Add(
            wx.StaticText(
                self,
                label="Target System:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.targetChoice = wx.Choice(
            self,
            choices=target_names,
        )

        form_sizer.Add(
            self.targetChoice,
            1,
            wx.EXPAND,
        )

        form_sizer.Add(
            wx.StaticText(
                self,
                label="Route Status:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.statusValues = [
            value
            for value, label
            in JUMP_STATUS_OPTIONS
        ]

        self.statusChoice = wx.Choice(
            self,
            choices=[
                label
                for value, label
                in JUMP_STATUS_OPTIONS
            ],
        )

        form_sizer.Add(
            self.statusChoice,
            1,
            wx.EXPAND,
        )

        main_sizer.Add(
            form_sizer,
            1,
            wx.ALL | wx.EXPAND,
            12,
            )

        button_sizer = (
            self.CreateButtonSizer(
                wx.OK | wx.CANCEL
            )
        )

        main_sizer.Add(
            button_sizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            12,
            )

        self.SetSizerAndFit(
            main_sizer
        )

        if target_name in target_names:
            self.targetChoice.SetSelection(
                target_names.index(
                    target_name
                )
            )
        elif target_names:
            self.targetChoice.SetSelection(
                0
            )

        if status in self.statusValues:
            self.statusChoice.SetSelection(
                self.statusValues.index(
                    status
                )
            )
        else:
            self.statusChoice.SetSelection(
                0
            )

    def getTargetName(self):
        return (
            self.targetChoice
            .GetStringSelection()
        )

    def getStatus(self):
        selection = (
            self.statusChoice
            .GetSelection()
        )

        if selection == wx.NOT_FOUND:
            return JumpLink.STATUS_NORMAL

        return self.statusValues[
            selection
        ]