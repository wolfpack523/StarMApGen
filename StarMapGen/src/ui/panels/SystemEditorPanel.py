import random
import re

import wx
from wx import StaticBoxSizer

from domain.StarSystem import StarSystem
from ui.panels.PlanetEditorPanel import (
    PlanetEditorPanel,
)
from ui.panels.JumpLinkEditorPanel import (
    JumpLinkEditorPanel,
)


class SystemEditorPanel(wx.Panel):
    """Editor for star systems, planets and jump links."""

    def __init__(
            self,
            parent,
            controller,
    ):
        super().__init__(
            parent
        )

        self.controller = controller

        self.selectedSystemIndex = (
            wx.NOT_FOUND
        )

        self.isCreatingSystem = False

        self.creationReturnIndex = (
            wx.NOT_FOUND
        )

        self.createControls()

    @property
    def params(self):
        return self.controller.params

    @property
    def starList(self):
        return self.controller.starList

    @starList.setter
    def starList(
            self,
            value,
    ):
        self.controller.starList = value

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

    def hasCurrentMapBounds(self):
        return (
            self.controller
            .hasCurrentMapBounds()
        )

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
        """Create the star system and jump link editor."""

        editor_sizer = wx.StaticBoxSizer(
            wx.VERTICAL,
            self,
            label="Star Systems",
        )

        self.createSystemListControls(editor_sizer)

        self.createSystemDetailsControls(editor_sizer)

        self.createSpectralTypeControls(editor_sizer)

        self.createSubEditors(editor_sizer)

        self.createSystemActionControls(editor_sizer)

        panel_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        panel_sizer.Add(
            editor_sizer,
            1,
            wx.EXPAND,
        )

        self.SetSizer(
            panel_sizer
        )

    def createSystemActionControls(self, editor_sizer: StaticBoxSizer):
        editor_button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.newSystemButton = wx.Button(
            self,
            label="New System",
        )

        self.newSystemButton.Bind(
            wx.EVT_BUTTON,
            self.beginNewSystem,
        )

        self.newSystemButton.Disable()

        editor_button_sizer.Add(
            self.newSystemButton,
            0,
            wx.RIGHT,
            5,
        )

        self.deleteSystemButton = wx.Button(
            self,
            label="Delete System",
        )

        self.deleteSystemButton.Bind(
            wx.EVT_BUTTON,
            self.deleteSelectedSystem,
        )

        self.deleteSystemButton.Disable()

        editor_button_sizer.Add(
            self.deleteSystemButton,
            0,
            wx.RIGHT,
            5,
        )

        self.cancelSystemButton = wx.Button(
            self,
            label="Cancel",
        )

        self.cancelSystemButton.Bind(
            wx.EVT_BUTTON,
            self.cancelNewSystem,
        )

        self.cancelSystemButton.Disable()

        editor_button_sizer.Add(
            self.cancelSystemButton,
            0,
            wx.RIGHT,
            5,
        )

        self.applySystemButton = wx.Button(
            self,
            label="Apply Changes",
        )

        self.applySystemButton.Bind(
            wx.EVT_BUTTON,
            self.applySystemChanges,
        )

        self.applySystemButton.Disable()

        editor_button_sizer.Add(
            self.applySystemButton,
            0,
        )

        editor_sizer.Add(
            editor_button_sizer,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
        )

    def createSubEditors(self, editor_sizer: StaticBoxSizer):
        self.planetEditor = (
            PlanetEditorPanel(
                self,
                self.onPlanetEditorChanged,
                self.SetStatusText,
            )
        )

        editor_sizer.Add(
            self.planetEditor,
            0,
            wx.EXPAND,
        )

        self.jumpEditor = (
            JumpLinkEditorPanel(
                self,
                self,
            )
        )

        editor_sizer.Add(
            self.jumpEditor,
            0,
            wx.EXPAND,
        )

    def createSpectralTypeControls(self, editor_sizer: StaticBoxSizer):
        spectral_help_sizer = wx.BoxSizer(wx.HORIZONTAL)

        spectral_hint = wx.StaticText(
            self,
            label=(
                "Separate spectral types with commas, "
                "semicolons, or new lines."
            ),
        )

        spectral_hint.Wrap(240)

        spectral_help_sizer.Add(
            spectral_hint,
            1,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.randomizeSpectralTypesButton = wx.Button(
            self,
            label="Randomize",
        )

        self.randomizeSpectralTypesButton.Bind(
            wx.EVT_BUTTON,
            self.randomizeSpectralTypes,
        )

        self.randomizeSpectralTypesButton.Disable()

        spectral_help_sizer.Add(
            self.randomizeSpectralTypesButton,
            0,
            wx.LEFT,
            5,
        )

        spectral_help_button = wx.Button(
            self,
            label="Spectral Type Help",
        )

        spectral_help_button.Bind(
            wx.EVT_BUTTON,
            self.showSpectralTypeHelp,
        )

        spectral_help_sizer.Add(
            spectral_help_button,
            0,
            wx.LEFT,
            5,
        )

        editor_sizer.Add(
            spectral_help_sizer,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
            5,
        )

    def createSystemDetailsControls(self, editor_sizer: StaticBoxSizer):
        details_sizer = wx.FlexGridSizer(
            cols=2,
            vgap=5,
            hgap=5,
        )

        details_sizer.AddGrowableCol(1, 1)

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Name:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemName = wx.TextCtrl(self)

        details_sizer.Add(
            self.systemName,
            1,
            wx.EXPAND,
        )

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Faction:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemFaction = wx.TextCtrl(
            self
        )

        details_sizer.Add(
            self.systemFaction,
            1,
            wx.EXPAND,
        )

        details_sizer.Add(
            wx.StaticText(
                self,
                label="X:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemX = wx.TextCtrl(self)

        details_sizer.Add(
            self.systemX,
            1,
            wx.EXPAND,
        )

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Y:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemY = wx.TextCtrl(self)

        details_sizer.Add(
            self.systemY,
            1,
            wx.EXPAND,
        )

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Z:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemZ = wx.TextCtrl(self)

        details_sizer.Add(
            self.systemZ,
            1,
            wx.EXPAND,
        )

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Number of Stars:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemStarCount = wx.TextCtrl(
            self,
            style=wx.TE_READONLY,
        )

        details_sizer.Add(
            self.systemStarCount,
            1,
            wx.EXPAND,
        )

        details_sizer.Add(
            wx.StaticText(
                self,
                label="Spectral Types:",
            ),
            0,
            wx.ALIGN_TOP,
        )

        self.systemSpectralTypes = wx.TextCtrl(
            self,
            size=(-1, 55),
            style=wx.TE_MULTILINE,
        )

        details_sizer.Add(
            self.systemSpectralTypes,
            1,
            wx.EXPAND,
        )

        editor_sizer.Add(
            details_sizer,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

    def createSystemListControls(self, editor_sizer: StaticBoxSizer):
        self.systemList = wx.ListBox(
            self,
            size=(340, 140),
            style=wx.LB_SINGLE,
        )

        self.systemList.Bind(
            wx.EVT_LISTBOX,
            self.onSystemSelected,
        )

        editor_sizer.Add(
            self.systemList,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

    def onPlanetEditorChanged(self):
        self.applySystemButton.Enable()

    def refreshSystemEditor(self, selected_index=0):
        """Refresh the system list from the current map state."""

        self.systemList.Freeze()

        try:
            self.systemList.Clear()

            for system in self.starList:
                self.systemList.Append(
                    f"{system.name} "
                    f"({system.x}, {system.y}, {system.z})"
                )
        finally:
            self.systemList.Thaw()

        self.newSystemButton.Enable(bool(self.params))

        if self.starList:
            selected_index = max(
                0,
                min(
                    selected_index,
                    len(self.starList) - 1,
                    ),
            )

            self.systemList.SetSelection(selected_index)
            self.showSystemDetails(selected_index)
        else:
            self.clearSystemDetails()

        self.Layout()
        self.refreshInputPanelLayout()

    def onSystemSelected(self, event):
        """Display the selected system."""

        if self.isCreatingSystem:
            return

        self.showSystemDetails(
            event.GetSelection()
        )

    def showSystemDetails(self, index):
        """Load one star system into the editor."""

        if (
                index == wx.NOT_FOUND
                or not 0 <= index < len(self.starList)
        ):
            self.clearSystemDetails()
            return

        self.leaveCreateMode()

        system = self.starList[index]
        self.selectedSystemIndex = index

        self.systemName.SetValue(system.name)
        self.systemFaction.SetValue(
            system.faction
        )
        self.systemX.SetValue(str(system.x))
        self.systemY.SetValue(str(system.y))
        self.systemZ.SetValue(str(system.z))
        self.systemStarCount.SetValue(
            str(system.nStars)
        )
        self.systemSpectralTypes.SetValue(
            ", ".join(system.stars)
        )

        self.planetEditor.setPlanets(
            system.planets
        )

        self.randomizeSpectralTypesButton.Enable()

        self.jumpEditor.setSystem(
            system.name
        )

        self.applySystemButton.SetLabel(
            "Apply Changes"
        )
        self.applySystemButton.Enable()
        self.deleteSystemButton.Enable()
        self.planetEditor.setEnabled(
            True
        )

    def beginNewSystem(self, event):
        """Switch the editor into creation mode."""

        if not self.params:
            wx.MessageBox(
                "Generate or load a map before adding a system.",
                "No map available",
                wx.OK | wx.ICON_INFORMATION,
                )
            return

        self.creationReturnIndex = (
            self.systemList.GetSelection()
        )

        current_selection = self.systemList.GetSelection()

        if current_selection != wx.NOT_FOUND:
            self.systemList.Deselect(current_selection)

        self.isCreatingSystem = True
        self.selectedSystemIndex = wx.NOT_FOUND

        self.systemList.Disable()
        self.newSystemButton.Disable()
        self.deleteSystemButton.Disable()
        self.cancelSystemButton.Enable()

        self.applySystemButton.SetLabel(
            "Create System"
        )
        self.applySystemButton.Enable()

        self.systemName.SetValue(
            self.createUniqueSystemName()
        )
        self.systemFaction.SetValue("")

        self.systemX.SetValue(
            str(
                min(
                    max(0, self.params["minX"]),
                    self.params["maxX"],
                )
            )
        )

        self.systemY.SetValue(
            str(
                min(
                    max(0, self.params["minY"]),
                    self.params["maxY"],
                )
            )
        )

        self.systemZ.SetValue(
            str(
                self.createRandomZCoordinate()
            )
        )

        self.systemStarCount.SetValue("1")
        self.systemSpectralTypes.SetValue(
            self.createRandomSpectralType()
        )

        self.randomizeSpectralTypesButton.Enable()

        self.planetEditor.setPlanets(
            []
        )

        self.planetEditor.setEnabled(
            True
        )

        # A new system may be linked to any existing system.
        self.jumpEditor.clear()

        self.systemName.SetFocus()
        self.systemName.SelectAll()

        self.SetStatusText(
            "Enter the values for the new star system."
        )

    def createRandomSpectralType(self):
        """Create a random main-sequence spectral type."""

        spectral_class = random.choices(
            population=[
                "O",
                "B",
                "A",
                "F",
                "G",
                "K",
                "M",
            ],
            weights=[
                1,
                3,
                6,
                10,
                15,
                25,
                40,
            ],
            k=1,
        )[0]

        spectral_subclass = random.randint(
            0,
            9,
        )

        return (
            f"{spectral_class}"
            f"{spectral_subclass}"
        )

    def randomizeSpectralTypes(self, event):
        """Randomize the spectral types currently shown in the editor."""

        current_value = (
            self.systemSpectralTypes
            .GetValue()
        )

        current_types = [
            item
            for item in re.split(
                r"[,;\r\n]+",
                current_value,
            )
            if item.strip()
        ]

        star_count = max(
            1,
            len(current_types),
        )

        spectral_types = [
            self.createRandomSpectralType()
            for _ in range(star_count)
        ]

        self.systemSpectralTypes.SetValue(
            ", ".join(spectral_types)
        )

        self.systemStarCount.SetValue(
            str(star_count)
        )

        self.SetStatusText(
            "Random spectral types generated. "
            "Use Apply Changes to save them."
        )

    def createRandomZCoordinate(self):
        """Create a random Z coordinate between -10 and +10."""

        minimum = max(
            -10,
            self.params["minZ"],
        )

        maximum = min(
            10,
            self.params["maxZ"],
        )

        if minimum <= maximum:
            return random.randint(
                minimum,
                maximum,
            )

        # The current map does not overlap the preferred -10..+10 range.
        return random.randint(
            self.params["minZ"],
            self.params["maxZ"],
        )

    def cancelNewSystem(self, event):
        """Cancel creation of a new system."""

        return_index = self.creationReturnIndex

        self.leaveCreateMode()

        if self.starList:
            if (
                    return_index == wx.NOT_FOUND
                    or return_index >= len(self.starList)
            ):
                return_index = 0

            self.systemList.SetSelection(return_index)
            self.showSystemDetails(return_index)
        else:
            self.clearSystemDetails()

        self.SetStatusText(
            "New star system creation cancelled."
        )

    def leaveCreateMode(self):
        """Restore the normal editor controls."""

        self.isCreatingSystem = False
        self.creationReturnIndex = wx.NOT_FOUND

        self.systemList.Enable()
        self.newSystemButton.Enable(bool(self.params))
        self.cancelSystemButton.Disable()

        self.applySystemButton.SetLabel(
            "Apply Changes"
        )

    def createUniqueSystemName(self):
        """Create the next available sequential system name."""

        existing_names = {
            system.name.casefold()
            for system in self.starList
        }

        highest_number = -1

        for system in self.starList:
            match = re.fullmatch(
                r"S(\d+)",
                system.name.strip(),
                re.IGNORECASE,
            )

            if match is None:
                continue

            highest_number = max(
                highest_number,
                int(match.group(1)),
            )

        next_number = highest_number + 1

        while (
                f"S{next_number:03d}".casefold()
                in existing_names
        ):
            next_number += 1

        return f"S{next_number:03d}"

    def applySystemChanges(self, event):
        """Create or update a star system."""

        if self.isCreatingSystem:
            self.createNewSystem()
        else:
            self.updateSelectedSystem()

    def createNewSystem(self):
        """Create a star system from the editor values."""

        try:
            values = self.readSystemEditorValues(
                wx.NOT_FOUND
            )
        except ValueError as error:
            self.showValidationError(error)
            return

        system = StarSystem(
            self.params,
            generate=False,
        )

        self.applyValuesToSystem(
            system,
            values,
        )

        self.starList.append(system)

        new_index = len(self.starList) - 1

        self.leaveCreateMode()
        self.saveAndRedrawCurrentMap()
        self.refreshSystemEditor(new_index)

        self.SetStatusText(
            f'Star system "{system.name}" was created.'
        )

    def updateSelectedSystem(self):
        """Update the currently selected star system."""

        index = self.selectedSystemIndex

        if (
                index == wx.NOT_FOUND
                or not 0 <= index < len(self.starList)
        ):
            wx.MessageBox(
                "Select a star system before applying changes.",
                "No star system selected",
                wx.OK | wx.ICON_INFORMATION,
                )
            return

        try:
            values = self.readSystemEditorValues(index)
        except ValueError as error:
            self.showValidationError(error)
            return

        system = self.starList[index]
        old_name = system.name

        self.applyValuesToSystem(
            system,
            values,
        )

        if old_name != system.name:
            for jump in self.jumpList:
                jump.renameSystem(
                    old_name,
                    system.name,
                )

        self.saveAndRedrawCurrentMap()
        self.refreshSystemEditor(index)

        self.SetStatusText(
            f'Changes to "{system.name}" were saved.'
        )

    def readSystemEditorValues(self, selected_index):
        """Validate and return all editable values."""

        if not self.hasCurrentMapBounds():
            raise ValueError(
                "No valid map bounds are available."
            )

        name = self.validateSystemName(
            self.systemName.GetValue(),
            selected_index,
        )

        faction = (
            self.systemFaction
            .GetValue()
            .strip()
        )

        if '"' in faction:
            raise ValueError(
                'The faction must not contain a double quote (").'
            )

        x = self.parseCoordinate(
            self.systemX.GetValue(),
            "X",
            self.params["minX"],
            self.params["maxX"],
        )

        y = self.parseCoordinate(
            self.systemY.GetValue(),
            "Y",
            self.params["minY"],
            self.params["maxY"],
        )

        z = self.parseCoordinate(
            self.systemZ.GetValue(),
            "Z",
            self.params["minZ"],
            self.params["maxZ"],
        )

        spectral_types = self.parseSpectralTypes(
            self.systemSpectralTypes.GetValue()
        )

        return {
            "name": name,
            "faction": faction,
            "x": x,
            "y": y,
            "z": z,
            "stars": spectral_types,
            "planets": (
                self.planetEditor
                .getPlanets()
            ),
        }

    def applyValuesToSystem(self, system, values):
        """Copy validated editor values into a system."""

        system.name = values["name"]
        system.faction = values["faction"]

        system.x = values["x"]
        system.y = values["y"]
        system.z = values["z"]

        system.mapPos = (
            system.x,
            system.y,
        )

        system.stars = values["stars"]
        system.nStars = len(system.stars)
        system.planets = values["planets"]

    def validateSystemName(
            self,
            value,
            selected_index=wx.NOT_FOUND,
    ):
        """Return a valid and unique system name."""

        name = value.strip()

        if not name:
            raise ValueError(
                "The system name must not be empty."
            )

        if '"' in name:
            raise ValueError(
                'The system name must not contain a double quote (").'
            )

        for index, system in enumerate(self.starList):
            if (
                    index != selected_index
                    and system.name == name
            ):
                raise ValueError(
                    f'A star system named "{name}" already exists.'
                )

        return name

    def parseCoordinate(
            self,
            value,
            label,
            minimum,
            maximum,
    ):
        """Parse and validate one coordinate."""

        try:
            coordinate = int(value.strip())
        except ValueError as error:
            raise ValueError(
                f"{label} must be a whole number."
            ) from error

        if not minimum <= coordinate <= maximum:
            raise ValueError(
                f"{label} must be between "
                f"{minimum} and {maximum}."
            )

        return coordinate

    def parseSpectralTypes(self, value):
        """Parse and validate the spectral type list."""

        spectral_types = [
            re.sub(
                r"\s+",
                "",
                item,
            ).upper()
            for item in re.split(
                r"[,;\r\n]+",
                value,
            )
            if item.strip()
        ]

        if not spectral_types:
            raise ValueError(
                "A star system must contain at least one star."
            )

        if len(spectral_types) > 10:
            raise ValueError(
                "The map renderer supports at most "
                "10 stars per system."
            )

        pattern = re.compile(
            r"^(?:"
            r"BD|WD|NS|BH|"
            r"[OBAFGKM][0-9]|"
            r"[FGKM][0-9](?:III|I)"
            r")$"
        )

        invalid_types = [
            spectralType
            for spectralType in spectral_types
            if pattern.fullmatch(spectralType) is None
        ]

        if invalid_types:
            invalid_text = ", ".join(invalid_types)

            raise ValueError(
                "Unsupported spectral type(s): "
                f"{invalid_text}.\n\n"
                "Use values such as G2, M4, K0III, M2I, "
                "BD, WD, NS, or BH."
            )

        return spectral_types

    def showValidationError(self, error):
        """Display a validation error."""

        wx.MessageBox(
            str(error),
            "Invalid star system data",
            wx.OK | wx.ICON_ERROR,
            )

    def showSpectralTypeHelp(self, event):
        """Show an explanation of the supported spectral types."""

        help_text = """SPECTRAL CLASSES

The first letter describes the spectral class and roughly the
temperature and colour of the star.

O  blue, extremely hot
B  blue-white
A  white
F  yellow-white
G  yellow
K  orange
M  red, comparatively cool

The sequence runs from hot to cool:

O - B - A - F - G - K - M


NUMBER

The number subdivides a spectral class from 0 to 9.

0 is the hotter end of the class.
9 is the cooler end of the class.

Examples:

G2  a relatively hot G-class star
G8  a cooler G-class star
M4  a red M-class star


LUMINOSITY CLASSES

No suffix
    Main-sequence star in this program.

III
    Giant star.

I
    Supergiant star.

Examples:

G2
    G-class main-sequence star.

K3III
    K-class giant.

M2I
    M-class supergiant.


SPECIAL TYPES

BD
    Brown dwarf.

WD
    White dwarf.

NS
    Neutron star.

BH
    Black hole.


SUPPORTED INPUT

Main-sequence stars:

O0-O9
B0-B9
A0-A9
F0-F9
G0-G9
K0-K9
M0-M9

Giants and supergiants:

F0III-F9III
G0III-G9III
K0III-K9III
M0III-M9III

F0I-F9I
G0I-G9I
K0I-K9I
M0I-M9I

Special objects:

BD, WD, NS, BH

Multiple stars may be separated with commas, semicolons,
or new lines.

Example:

G2, M4, WD
"""

        dialog = wx.Dialog(
            self,
            title="Spectral Type Help",
            size=(560, 620),
            style=(
                    wx.DEFAULT_DIALOG_STYLE
                    | wx.RESIZE_BORDER
            ),
        )

        dialog_sizer = wx.BoxSizer(wx.VERTICAL)

        help_field = wx.TextCtrl(
            dialog,
            value=help_text,
            style=(
                    wx.TE_MULTILINE
                    | wx.TE_READONLY
                    | wx.TE_RICH2
            ),
        )

        dialog_sizer.Add(
            help_field,
            1,
            wx.ALL | wx.EXPAND,
            10,
            )

        close_button = wx.Button(
            dialog,
            wx.ID_OK,
            label="Close",
        )

        dialog_sizer.Add(
            close_button,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT,
            10,
            )

        dialog.SetSizer(dialog_sizer)

        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()


    def clearSystemDetails(self):
        """Clear the system editor."""

        self.leaveCreateMode()
        self.selectedSystemIndex = wx.NOT_FOUND

        self.systemName.SetValue("")
        self.systemFaction.SetValue("")
        self.systemX.SetValue("")
        self.systemY.SetValue("")
        self.systemZ.SetValue("")
        self.systemStarCount.SetValue("")
        self.systemSpectralTypes.SetValue("")
        self.randomizeSpectralTypesButton.Disable()

        self.jumpEditor.clear()

        self.planetEditor.clear()

        self.applySystemButton.Disable()
        self.cancelSystemButton.Disable()

        self.newSystemButton.Enable(bool(self.params))

    def deleteSelectedSystem(self, event):
        """Delete the selected star system and all of its jump links."""

        if self.isCreatingSystem:
            return

        index = self.selectedSystemIndex

        if (
                index == wx.NOT_FOUND
                or not 0 <= index < len(self.starList)
        ):
            wx.MessageBox(
                "Select a star system before deleting it.",
                "No Star System Selected",
                wx.OK | wx.ICON_INFORMATION,
                )
            return

        system = self.starList[index]

        connected_links = [
            jump
            for jump in self.jumpList
            if jump.contains(system.name)
        ]

        message = (
            f'Delete the star system "{system.name}"?'
        )

        if connected_links:
            link_word = (
                "jump link"
                if len(connected_links) == 1
                else "jump links"
            )

            message += (
                f"\n\n{len(connected_links)} {link_word} "
                "connected to this system will also be deleted."
            )

        message += "\n\nThis action cannot be undone."

        result = wx.MessageBox(
            message,
            "Delete Star System",
            wx.YES_NO
            | wx.NO_DEFAULT
            | wx.ICON_WARNING,
            )

        if result != wx.YES:
            return

        deleted_name = system.name

        # Remove every jump link involving the deleted system.
        self.jumpList = [
            jump
            for jump in self.jumpList
            if not jump.contains(deleted_name)
        ]

        # Remove the actual star system.
        del self.starList[index]

        self.selectedSystemIndex = wx.NOT_FOUND

        self.saveAndRedrawCurrentMap()

        if self.starList:
            # Select the next system. If the deleted system was the
            # final entry, select the new final entry instead.
            next_index = min(
                index,
                len(self.starList) - 1,
                )

            self.refreshSystemEditor(next_index)
        else:
            self.refreshSystemEditor()

        self.SetStatusText(
            f'Star system "{deleted_name}" and '
            f"{len(connected_links)} connected jump link(s) "
            "were deleted."
        )

    def resetState(self):
        """Reset temporary system editor state."""

        self.selectedSystemIndex = (
            wx.NOT_FOUND
        )

        self.isCreatingSystem = False

        self.creationReturnIndex = (
            wx.NOT_FOUND
        )

        self.planetEditor.clear()
        self.jumpEditor.clear()