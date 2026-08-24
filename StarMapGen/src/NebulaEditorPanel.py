import re

import wx
from wx.lib.masked import NumCtrl

from Nebula import Nebula


class NebulaEditorPanel(wx.Panel):
    """Editor for nebula regions."""

    def __init__(
            self,
            parent,
            controller,
    ):
        super().__init__(parent)

        self.controller = controller

        self.selectedNebulaIndex = (
            wx.NOT_FOUND
        )

        self.isCreatingNebula = False

        self.nebulaCreationReturnIndex = (
            wx.NOT_FOUND
        )

        self.createControls()

    @property
    def params(self):
        return self.controller.params

    @property
    def nebulaList(self):
        return self.controller.nebulaList

    @nebulaList.setter
    def nebulaList(
            self,
            value,
    ):
        self.controller.nebulaList = value

    def saveAndRedrawCurrentMap(self):
        self.controller.saveAndRedrawCurrentMap()

    def refreshInputPanelLayout(self):
        self.controller.refreshInputPanelLayout()

    def SetStatusText(
            self,
            text,
    ):
        self.controller.SetStatusText(
            text
        )

    def createControls(self):
        """Create the nebula editor."""
        panel_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        self.nebulaListControl = wx.ListBox(
            self,
            size=(340, 110),
            style=wx.LB_SINGLE,
        )

        self.nebulaListControl.Bind(
            wx.EVT_LISTBOX,
            self.onNebulaSelected,
        )

        panel_sizer.Add(
            self.nebulaListControl,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        details_sizer = wx.FlexGridSizer(
            cols=2,
            vgap=5,
            hgap=5,
        )

        details_sizer.AddGrowableCol(
            1,
            1,
        )

        # ------------------------------------------------------------
        # Name
        # ------------------------------------------------------------

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Name:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nebulaName = wx.TextCtrl(
            self
        )

        details_sizer.Add(
            self.nebulaName,
            1,
            wx.EXPAND,
        )

        # ------------------------------------------------------------
        # Style
        # ------------------------------------------------------------

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Style:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nebulaStyleValues = [
            Nebula.STYLE_CLOUD,
            Nebula.STYLE_OUTLINE,
            Nebula.STYLE_HAZE,
        ]

        self.nebulaStyle = wx.Choice(
            self,
            choices=[
                "Cloud",
                "Outline",
                "Haze",
            ],
        )

        self.nebulaStyle.SetSelection(0)

        details_sizer.Add(
            self.nebulaStyle,
            1,
            wx.EXPAND,
        )

        # ------------------------------------------------------------
        # Color
        # ------------------------------------------------------------

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Color:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nebulaColor = wx.TextCtrl(
            self
        )

        details_sizer.Add(
            self.nebulaColor,
            1,
            wx.EXPAND,
        )

        # ------------------------------------------------------------
        # Opacity
        # ------------------------------------------------------------

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Opacity:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nebulaOpacity = NumCtrl(
            self,
            min=0.0,
            max=1.0,
            fractionWidth=2,
        )

        details_sizer.Add(
            self.nebulaOpacity,
            1,
            wx.EXPAND,
        )

        panel_sizer.Add(
            details_sizer,
            0,
            wx.ALL | wx.EXPAND,
            5,
            )

        # ------------------------------------------------------------
        # Points
        # ------------------------------------------------------------

        panel_sizer.Add(
            wx.StaticText(
                self,
                label="Points:",
            ),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            5,
            )

        self.nebulaPoints = wx.TextCtrl(
            self,
            size=(-1, 100),
            style=wx.TE_MULTILINE,
        )

        panel_sizer.Add(
            self.nebulaPoints,
            0,
            wx.LEFT | wx.RIGHT | wx.EXPAND,
            5,
            )

        point_hint = wx.StaticText(
            self,
            label=(
                "Enter one boundary point per line as x,y. "
                "Points are connected in the entered order."
            ),
        )

        point_hint.Wrap(330)

        panel_sizer.Add(
            point_hint,
            0,
            wx.ALL | wx.EXPAND,
            5,
            )

        # ------------------------------------------------------------
        # Buttons
        # ------------------------------------------------------------

        button_sizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        self.newNebulaButton = wx.Button(
            self,
            label="New Nebula",
        )

        self.newNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.beginNewNebula,
        )

        self.newNebulaButton.Disable()

        button_sizer.Add(
            self.newNebulaButton,
            0,
            wx.RIGHT,
            5,
        )

        self.deleteNebulaButton = wx.Button(
            self,
            label="Delete Nebula",
        )

        self.deleteNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.deleteSelectedNebula,
        )

        self.deleteNebulaButton.Disable()

        button_sizer.Add(
            self.deleteNebulaButton,
            0,
            wx.RIGHT,
            5,
        )

        self.cancelNebulaButton = wx.Button(
            self,
            label="Cancel",
        )

        self.cancelNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.cancelNewNebula,
        )

        self.cancelNebulaButton.Disable()

        button_sizer.Add(
            self.cancelNebulaButton,
            0,
            wx.RIGHT,
            5,
        )

        self.applyNebulaButton = wx.Button(
            self,
            label="Apply Changes",
        )

        self.applyNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.applyNebulaChanges,
        )

        self.applyNebulaButton.Disable()

        button_sizer.Add(
            self.applyNebulaButton,
            0,
        )

        panel_sizer.Add(
            button_sizer,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
            )

        self.SetSizer(
            panel_sizer
        )

        self.clearNebulaDetails()

    def refreshNebulaEditor(
            self,
            selected_index=0,
    ):
        """Refresh the nebula list."""

        self.nebulaListControl.Freeze()

        try:
            self.nebulaListControl.Clear()

            for nebula in self.nebulaList:
                self.nebulaListControl.Append(
                    f"{nebula.name} "
                    f"({len(nebula.points)} points)"
                )

        finally:
            self.nebulaListControl.Thaw()

        self.newNebulaButton.Enable(
            bool(self.params)
        )

        if self.nebulaList:
            selected_index = max(
                0,
                min(
                    selected_index,
                    len(self.nebulaList) - 1,
                    ),
            )

            self.nebulaListControl.SetSelection(
                selected_index
            )

            self.showNebulaDetails(
                selected_index
            )

        else:
            self.clearNebulaDetails()

        self.refreshInputPanelLayout()

    def onNebulaSelected(self, event):
        """Display the selected nebula."""

        if self.isCreatingNebula:
            return

        self.showNebulaDetails(
            event.GetSelection()
        )

    def showNebulaDetails(self, index):
        """Load a nebula into the editor."""

        if (
                index == wx.NOT_FOUND
                or not 0 <= index < len(self.nebulaList)
        ):
            self.clearNebulaDetails()
            return

        self.leaveNebulaCreateMode()

        nebula = self.nebulaList[index]

        self.selectedNebulaIndex = index

        self.nebulaName.SetValue(
            nebula.name
        )

        if nebula.style in self.nebulaStyleValues:
            self.nebulaStyle.SetSelection(
                self.nebulaStyleValues.index(
                    nebula.style
                )
            )
        else:
            self.nebulaStyle.SetSelection(0)

        self.nebulaColor.SetValue(
            nebula.color
        )

        self.nebulaOpacity.SetValue(
            nebula.opacity
        )

        self.nebulaPoints.SetValue(
            "\n".join(
                f"{x},{y}"
                for x, y in nebula.points
            )
        )

        self.applyNebulaButton.SetLabel(
            "Apply Changes"
        )

        self.applyNebulaButton.Enable()
        self.deleteNebulaButton.Enable()

    def beginNewNebula(self, event):
        """Switch the nebula editor into creation mode."""

        if not self.params:
            wx.MessageBox(
                "Generate or load a map before adding a nebula.",
                "No map available",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        self.nebulaCreationReturnIndex = (
            self.nebulaListControl.GetSelection()
        )

        current_selection = (
            self.nebulaListControl.GetSelection()
        )

        if current_selection != wx.NOT_FOUND:
            self.nebulaListControl.Deselect(
                current_selection
            )

        self.isCreatingNebula = True
        self.selectedNebulaIndex = wx.NOT_FOUND

        self.nebulaListControl.Disable()
        self.newNebulaButton.Disable()
        self.deleteNebulaButton.Disable()

        self.cancelNebulaButton.Enable()

        self.applyNebulaButton.SetLabel(
            "Create Nebula"
        )

        self.applyNebulaButton.Enable()

        self.nebulaName.SetValue(
            self.createUniqueNebulaName()
        )

        self.nebulaStyle.SetSelection(0)

        self.nebulaColor.SetValue(
            "#7a2f8f"
        )

        self.nebulaOpacity.SetValue(
            0.35
        )

        self.nebulaPoints.SetValue("")

        self.nebulaName.SetFocus()
        self.nebulaName.SelectAll()

        self.SetStatusText(
            "Enter the values for the new nebula."
        )

    def createUniqueNebulaName(self):
        """Create a unique default nebula name."""

        existing_names = {
            nebula.name.casefold()
            for nebula in self.nebulaList
        }

        base_name = "Nebula"

        if base_name.casefold() not in existing_names:
            return base_name

        number = 2

        while (
                f"{base_name} {number}".casefold()
                in existing_names
        ):
            number += 1

        return f"{base_name} {number}"

    def cancelNewNebula(self, event):
        """Cancel creation of a nebula."""

        return_index = (
            self.nebulaCreationReturnIndex
        )

        self.leaveNebulaCreateMode()

        if self.nebulaList:
            if (
                    return_index == wx.NOT_FOUND
                    or return_index >= len(self.nebulaList)
            ):
                return_index = 0

            self.nebulaListControl.SetSelection(
                return_index
            )

            self.showNebulaDetails(
                return_index
            )

        else:
            self.clearNebulaDetails()

        self.SetStatusText(
            "Nebula creation canpointed."
        )

    def leaveNebulaCreateMode(self):
        """Restore the normal nebula editor controls."""

        self.isCreatingNebula = False
        self.nebulaCreationReturnIndex = (
            wx.NOT_FOUND
        )

        self.nebulaListControl.Enable()

        self.newNebulaButton.Enable(
            bool(self.params)
        )

        self.cancelNebulaButton.Disable()

        self.applyNebulaButton.SetLabel(
            "Apply Changes"
        )

    def readNebulaEditorValues(
            self,
            selected_index,
    ):
        """Validate and return the nebula editor values."""

        name = self.validateNebulaName(
            self.nebulaName.GetValue(),
            selected_index,
        )

        style_selection = (
            self.nebulaStyle.GetSelection()
        )

        if style_selection == wx.NOT_FOUND:
            raise ValueError(
                "Select a nebula style."
            )

        style = self.nebulaStyleValues[
            style_selection
        ]

        color = self.parseNebulaColor(
            self.nebulaColor.GetValue()
        )

        opacity = float(
            self.nebulaOpacity.GetValue()
        )

        if not 0.0 <= opacity <= 1.0:
            raise ValueError(
                "Opacity must be between 0 and 1."
            )

        points = self.parseNebulaPoints(
            self.nebulaPoints.GetValue()
        )

        return {
            "name": name,
            "style": style,
            "color": color,
            "opacity": opacity,
            "points": points,
        }

    def validateNebulaName(
            self,
            value,
            selected_index=wx.NOT_FOUND,
    ):
        """Validate a nebula name."""

        name = value.strip()

        if not name:
            raise ValueError(
                "The nebula name must not be empty."
            )

        if '"' in name:
            raise ValueError(
                'The nebula name must not contain a double quote (").'
            )

        for index, nebula in enumerate(
                self.nebulaList
        ):
            if (
                    index != selected_index
                    and nebula.name.casefold()
                    == name.casefold()
            ):
                raise ValueError(
                    f'A nebula named "{name}" already exists.'
                )

        return name

    def parseNebulaColor(self, value):
        """Validate an SVG hexadecimal colour."""

        color = value.strip()

        if re.fullmatch(
                r"#[0-9a-fA-F]{6}",
                color,
        ) is None:
            raise ValueError(
                "Nebula color must be a hexadecimal "
                "RGB value such as #7a2f8f."
            )

        return color.lower()

    def parseNebulaPoints(self, value):
        """Parse the ordered boundary points from the nebula editor."""

        points = []

        lines = value.splitlines()

        for line_number, raw_line in enumerate(
                lines,
                start=1,
        ):
            line = raw_line.strip()

            if not line:
                continue

            match = re.fullmatch(
                r"\(?\s*(-?\d+)\s*,\s*(-?\d+)\s*\)?",
                line,
            )

            if match is None:
                raise ValueError(
                    "Invalid nebula point on line "
                    f"{line_number}: {raw_line}\n\n"
                    "Use one point per line in the form x,y."
                )

            x = int(
                match.group(1)
            )

            y = int(
                match.group(2)
            )

            if not (
                    self.params["minX"]
                    <= x
                    <= self.params["maxX"]
            ):
                raise ValueError(
                    f"Nebula point X coordinate {x} "
                    "is outside the current map bounds "
                    f"({self.params['minX']} to "
                    f"{self.params['maxX']})."
                )

            if not (
                    self.params["minY"]
                    <= y
                    <= self.params["maxY"]
            ):
                raise ValueError(
                    f"Nebula point Y coordinate {y} "
                    "is outside the current map bounds "
                    f"({self.params['minY']} to "
                    f"{self.params['maxY']})."
                )

            point = (
                x,
                y,
            )

            if point in points:
                raise ValueError(
                    f"Nebula point {x},{y} is duplicated."
                )

            points.append(
                point
            )

        if len(points) < 3:
            raise ValueError(
                "A nebula must contain at least three boundary points."
            )

        return points

    def applyNebulaChanges(self, event):
        """Create or update a nebula."""

        if self.isCreatingNebula:
            self.createNewNebula()
        else:
            self.updateSelectedNebula()

    def createNewNebula(self):
        """Create a nebula from the editor values."""

        try:
            values = self.readNebulaEditorValues(
                wx.NOT_FOUND
            )
        except ValueError as error:
            self.showNebulaValidationError(
                error
            )
            return

        nebula = Nebula(
            name=values["name"],
            points=values["points"],
            style=values["style"],
            color=values["color"],
            opacity=values["opacity"],
        )

        self.nebulaList.append(
            nebula
        )

        new_index = (
                len(self.nebulaList) - 1
        )

        self.leaveNebulaCreateMode()
        self.saveAndRedrawCurrentMap()
        self.refreshNebulaEditor(
            new_index
        )

        self.SetStatusText(
            f'Nebula "{nebula.name}" was created.'
        )

    def updateSelectedNebula(self):
        """Update the selected nebula."""

        index = self.selectedNebulaIndex

        if (
                index == wx.NOT_FOUND
                or not 0 <= index < len(self.nebulaList)
        ):
            wx.MessageBox(
                "Select a nebula before applying changes.",
                "No nebula selected",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        try:
            values = self.readNebulaEditorValues(
                index
            )
        except ValueError as error:
            self.showNebulaValidationError(
                error
            )
            return

        nebula = self.nebulaList[index]

        nebula.name = values["name"]
        nebula.style = values["style"]
        nebula.color = values["color"]
        nebula.opacity = values["opacity"]
        nebula.points = values["points"]

        self.saveAndRedrawCurrentMap()

        self.refreshNebulaEditor(
            index
        )

        self.SetStatusText(
            f'Changes to nebula "{nebula.name}" were applied.'
        )

    def deleteSelectedNebula(self, event):
        """Delete the selected nebula."""

        index = self.selectedNebulaIndex

        if (
                index == wx.NOT_FOUND
                or not 0 <= index < len(self.nebulaList)
        ):
            return

        nebula = self.nebulaList[index]

        answer = wx.MessageBox(
            (
                f'Delete nebula "{nebula.name}"?'
            ),
            "Delete Nebula",
            wx.YES_NO
            | wx.NO_DEFAULT
            | wx.ICON_WARNING,
        )

        if answer != wx.YES:
            return

        del self.nebulaList[index]

        self.saveAndRedrawCurrentMap()
        if self.nebulaList:
            next_index = min(
                index,
                len(self.nebulaList) - 1,
            )

            self.refreshNebulaEditor(
                next_index
            )
        else:
            self.refreshNebulaEditor()

        self.SetStatusText(
            f'Nebula "{nebula.name}" was deleted.'
        )

    def clearNebulaDetails(self):
        """Clear and disable the nebula editor."""

        self.isCreatingNebula = False
        self.nebulaCreationReturnIndex = (
            wx.NOT_FOUND
        )

        self.selectedNebulaIndex = (
            wx.NOT_FOUND
        )

        self.nebulaName.SetValue("")
        self.nebulaStyle.SetSelection(0)
        self.nebulaColor.SetValue(
            "#7a2f8f"
        )
        self.nebulaOpacity.SetValue(
            0.35
        )
        self.nebulaPoints.SetValue("")

        self.nebulaListControl.Enable()

        self.newNebulaButton.Enable(
            bool(self.params)
        )

        self.deleteNebulaButton.Disable()
        self.cancelNebulaButton.Disable()
        self.applyNebulaButton.Disable()

        self.applyNebulaButton.SetLabel(
            "Apply Changes"
        )

    def showNebulaValidationError(
            self,
            error,
    ):
        """Display a nebula validation error."""

        wx.MessageBox(
            str(error),
            "Invalid nebula data",
            wx.OK | wx.ICON_ERROR,
        )
    def resetState(self):
        """Reset temporary nebula editor state."""

        self.selectedNebulaIndex = (
            wx.NOT_FOUND
        )
    
        self.isCreatingNebula = False
    
        self.nebulaCreationReturnIndex = (
            wx.NOT_FOUND
        )