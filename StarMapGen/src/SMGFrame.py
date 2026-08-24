import re
import threading

import wx
import wx.lib.intctrl
import wx.lib.scrolledpanel
from wx.lib.masked import NumCtrl

from loadData import loadData
from makeMap import (
    createMap as writeSvgMap,
    createMapSymbols,
    createSystems,
    findConnections,
    findJumps,
    findOverlaps,
)
from SMGMapPanel import SMGMapPanel
from StarSystem import StarSystem
from writeData import (
    writeConnectionData,
    writeNebulaData,
    writePlanetData,
    writeSystemData, writeFactionData,
)
from Nebula import Nebula
from exportPng import exportPng
from JumpLinkDialog import (
    JUMP_STATUS_OPTIONS,
)
from SystemEditorPanel import (
    SystemEditorPanel,
)

JUMP_STATUS_LABELS = dict(
    JUMP_STATUS_OPTIONS
)

class SMGFrame(wx.Frame):
    def __init__(self):
        super().__init__(
            parent=None,
            title="Star Map Generator",
        )

        self.CreateStatusBar()

        # Current map state
        self.params = {}
        self.starList = []
        self.jumpList = []
        self.nebulaList = []

        # Editor state
        self.selectedNebulaIndex = wx.NOT_FOUND
        self.isCreatingNebula = False
        self.nebulaCreationReturnIndex = wx.NOT_FOUND

        self.Center()

        mainPanel = wx.Panel(self)

        # Sizer for the entire window
        self.mainSizer = wx.BoxSizer(wx.HORIZONTAL)

        # Scrollable left side
        self.inputPanel = wx.lib.scrolledpanel.ScrolledPanel(
            mainPanel,
            style=wx.TAB_TRAVERSAL | wx.VSCROLL,
        )

        # This sizer belongs to the scrolling panel itself.
        scrollSizer = wx.BoxSizer(wx.HORIZONTAL)

        # All actual input controls are placed in this sizer.
        inputSizer = wx.BoxSizer(wx.VERTICAL)

        self.createParameterControls(
            self.inputPanel,
            inputSizer,
        )

        self.createMapBoundsControls(
            self.inputPanel,
            inputSizer,
        )

        self.systemEditor = (
            SystemEditorPanel(
                self.inputPanel,
                self,
            )
        )

        inputSizer.Add(
            self.systemEditor,
            0,
            wx.TOP | wx.EXPAND,
            5,
        )

        self.createNebulaEditor(
            self.inputPanel,
            inputSizer,
        )

        # Reserve space on the right so that the scrollbar does not
        # cover the contents.
        scrollbarWidth = wx.SystemSettings.GetMetric(
            wx.SYS_VSCROLL_X
        )

        if scrollbarWidth <= 0:
            scrollbarWidth = 20

        scrollSizer.Add(
            inputSizer,
            1,
            wx.RIGHT | wx.EXPAND,
            scrollbarWidth + 5,
        )

        self.inputPanel.SetSizer(
            scrollSizer
        )

        self.inputPanel.SetupScrolling(
            scroll_x=False,
            scroll_y=True,
            rate_y=20,
        )

        self.updateInputPanelMinimumWidth()

        self.mainSizer.Add(
            self.inputPanel,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        # Map display area
        mapSizer = wx.FlexGridSizer(
            rows=1,
            cols=1,
            vgap=0,
            hgap=0,
        )

        mapSizer.AddGrowableCol(0)
        mapSizer.AddGrowableRow(0)
        mapSizer.SetFlexibleDirection(wx.BOTH)

        self.mapPanel = SMGMapPanel(mainPanel)

        mapSizer.Add(
            self.mapPanel,
            1,
            wx.ALL | wx.EXPAND,
            5,
        )

        self.mainSizer.Add(
            mapSizer,
            1,
            wx.ALL | wx.EXPAND,
            5,
        )

        self.setDefaults()

        mainPanel.SetSizer(
            self.mainSizer
        )

        # Do not calculate the minimum window size from all controls.
        # The left side is scrollable now.
        self.SetMinSize(
            (900, 520)
        )

        self.SetSize(
            (1200, 760)
        )

        mainPanel.Layout()
        self.inputPanel.FitInside()

        self.Bind(
            wx.EVT_SIZE,
            self.onResize,
        )

        self.Show()

    def createCollapsibleSection(
            self,
            parent,
            targetSizer,
            label,
            expanded=False,
    ):
        """Create one collapsible section in the input panel."""

        pane = wx.CollapsiblePane(
            parent,
            label=label,
            style=(
                    wx.CP_DEFAULT_STYLE
                    | wx.CP_NO_TLW_RESIZE
            ),
        )

        pane.Collapse(
            not expanded
        )

        pane.Bind(
            wx.EVT_COLLAPSIBLEPANE_CHANGED,
            self.onCollapsiblePaneChanged,
        )

        targetSizer.Add(
            pane,
            0,
            wx.BOTTOM | wx.EXPAND,
            5,
        )

        contentPanel = pane.GetPane()

        contentSizer = wx.BoxSizer(
            wx.VERTICAL
        )

        contentPanel.SetSizer(
            contentSizer
        )

        return (
            pane,
            contentPanel,
            contentSizer,
        )

    def onCollapsiblePaneChanged(self, event):
        """Recalculate the scrollable area after expanding a section."""

        self.refreshInputPanelLayout()
        event.Skip()

    def updateInputPanelMinimumWidth(self):
        """Calculate the required width of the scrollable input panel."""

        if not hasattr(self, "inputPanel"):
            return

        panelSizer = self.inputPanel.GetSizer()

        if panelSizer is None:
            return

        minimumWidth = (
            panelSizer.GetMinSize().GetWidth()
        )

        borderWidth = (
            self.inputPanel
            .GetWindowBorderSize()
            .GetWidth()
        )

        self.inputPanel.SetMinSize(
            (
                minimumWidth
                + borderWidth
                + 5,
                -1,
            )
        )

    def refreshInputPanelLayout(self):
        """Update the input panel layout and its scrollbars."""

        if not hasattr(
                self,
                "inputPanel",
        ):
            return

        self.inputPanel.Layout()
        self.inputPanel.FitInside()

        self.updateInputPanelMinimumWidth()

        self.mainSizer.Layout()

    def createParameterControls(
            self,
            parent,
            inputSizer,
    ):
        """Create collapsible file and random generation sections."""

        def addControlRow(
                sectionParent,
                sectionSizer,
                label,
                control,
        ):
            row = wx.BoxSizer(
                wx.HORIZONTAL
            )

            row.Add(
                wx.StaticText(
                    sectionParent,
                    label=label,
                ),
                0,
                wx.ALIGN_CENTER_VERTICAL
                | wx.RIGHT,
                8,
            )

            row.Add(
                control,
                1,
                wx.EXPAND,
            )

            sectionSizer.Add(
                row,
                0,
                wx.ALL | wx.EXPAND,
                5,
            )

        # ------------------------------------------------------------
        # Map files and display
        # ------------------------------------------------------------

        (
            self.mapFilesPane,
            filesParent,
            filesSizer,
        ) = self.createCollapsibleSection(
            parent,
            inputSizer,
            "Map Files and Display",
            expanded=True,
        )

        self.textScale = NumCtrl(
            filesParent,
            min=0.25,
            fractionWidth=2,
        )

        addControlRow(
            filesParent,
            filesSizer,
            "Text Scale:",
            self.textScale,
        )

        self.outMapName = wx.TextCtrl(
            filesParent
        )

        addControlRow(
            filesParent,
            filesSizer,
            "Output Map Filename:",
            self.outMapName,
        )

        self.dataName = wx.TextCtrl(
            filesParent
        )

        addControlRow(
            filesParent,
            filesSizer,
            "Data Filename:",
            self.dataName,
        )

        printZRow = wx.BoxSizer(
            wx.HORIZONTAL
        )

        printZRow.Add(
            wx.StaticText(
                filesParent,
                label="Print Z coordinate:",
            ),
            1,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.printZ = wx.CheckBox(
            filesParent
        )

        printZRow.Add(
            self.printZ,
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        filesSizer.Add(
            printZRow,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        fileButtonSizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        loadButton = wx.Button(
            filesParent,
            label="Load Map",
        )

        loadButton.Bind(
            wx.EVT_BUTTON,
            self.loadMap,
        )

        fileButtonSizer.Add(
            loadButton,
            0,
            wx.RIGHT,
            5,
        )

        self.exportPngButton = wx.Button(
            filesParent,
            label="Export PNG",
        )

        self.exportPngButton.Bind(
            wx.EVT_BUTTON,
            self.onExportPng,
        )

        self.exportPngButton.Disable()

        fileButtonSizer.Add(
            self.exportPngButton,
            0,
            wx.RIGHT,
            5,
        )

        resetButton = wx.Button(
            filesParent,
            label="Reset Values",
        )

        resetButton.Bind(
            wx.EVT_BUTTON,
            self.resetParameters,
        )

        fileButtonSizer.Add(
            resetButton,
            0,
        )

        filesSizer.Add(
            fileButtonSizer,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
        )

        # ------------------------------------------------------------
        # Random generation
        # ------------------------------------------------------------

        (
            self.randomGenerationPane,
            randomParent,
            randomSizer,
        ) = self.createCollapsibleSection(
            parent,
            inputSizer,
            "Random Generation",
            expanded=False,
        )

        self.xSize = wx.lib.intctrl.IntCtrl(
            randomParent,
            min=1,
        )

        addControlRow(
            randomParent,
            randomSizer,
            "Map Width (x):",
            self.xSize,
        )

        self.ySize = wx.lib.intctrl.IntCtrl(
            randomParent,
            min=1,
        )

        addControlRow(
            randomParent,
            randomSizer,
            "Map Height (y):",
            self.ySize,
        )

        self.zSize = wx.lib.intctrl.IntCtrl(
            randomParent,
            min=1,
        )

        addControlRow(
            randomParent,
            randomSizer,
            "Map Thickness (z):",
            self.zSize,
        )

        self.stellarDensity = NumCtrl(
            randomParent,
            min=0,
            fractionWidth=4,
        )

        addControlRow(
            randomParent,
            randomSizer,
            "Stellar Density:",
            self.stellarDensity,
        )

        generateButton = wx.Button(
            randomParent,
            label="Generate Random Map",
        )

        generateButton.Bind(
            wx.EVT_BUTTON,
            self.generateMap,
        )

        randomSizer.Add(
            generateButton,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
        )

    def createMapBoundsControls(
            self,
            parent,
            inputSizer,
    ):
        """Create collapsible controls for extending the map."""

        (
            self.mapBoundsPane,
            boundsParent,
            boundsSizer,
        ) = self.createCollapsibleSection(
            parent,
            inputSizer,
            "Map Bounds",
            expanded=False,
        )

        self.mapBoundsLabel = wx.StaticText(
            boundsParent,
            label="No map loaded.",
        )

        self.mapBoundsLabel.Wrap(
            330
        )

        boundsSizer.Add(
            self.mapBoundsLabel,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        amountSizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        amountSizer.Add(
            wx.StaticText(
                boundsParent,
                label="Extend by:",
            ),
            1,
            wx.ALIGN_CENTER_VERTICAL
            | wx.RIGHT,
            5,
        )

        self.extendAmount = wx.lib.intctrl.IntCtrl(
            boundsParent,
            min=1,
        )

        self.extendAmount.SetValue(
            5
        )

        self.extendAmount.Disable()

        amountSizer.Add(
            self.extendAmount,
            0,
        )

        boundsSizer.Add(
            amountSizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
        )

        buttonGrid = wx.GridSizer(
            rows=2,
            cols=3,
            vgap=5,
            hgap=5,
        )

        buttonDefinitions = [
            ("X -", "x-"),
            ("Y -", "y-"),
            ("Z -", "z-"),
            ("X +", "x+"),
            ("Y +", "y+"),
            ("Z +", "z+"),
        ]

        self.mapBoundsButtons = []

        for label, direction in buttonDefinitions:
            button = wx.Button(
                boundsParent,
                label=label,
            )

            button.Bind(
                wx.EVT_BUTTON,
                lambda event, value=direction:
                self.extendMap(value),
            )

            button.Disable()

            self.mapBoundsButtons.append(
                button
            )

            buttonGrid.Add(
                button,
                1,
                wx.EXPAND,
            )

        boundsSizer.Add(
            buttonGrid,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
        )


    def createNebulaEditor(
            self,
            parent,
            inputSizer,
    ):
        """Create the nebula editor."""

        (
            self.nebulaPane,
            nebulaParent,
            nebulaSizer,
        ) = self.createCollapsibleSection(
            parent,
            inputSizer,
            "Nebulae",
            expanded=False,
        )

        self.nebulaListControl = wx.ListBox(
            nebulaParent,
            size=(340, 110),
            style=wx.LB_SINGLE,
        )

        self.nebulaListControl.Bind(
            wx.EVT_LISTBOX,
            self.onNebulaSelected,
        )

        nebulaSizer.Add(
            self.nebulaListControl,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        detailsSizer = wx.FlexGridSizer(
            cols=2,
            vgap=5,
            hgap=5,
        )

        detailsSizer.AddGrowableCol(
            1,
            1,
        )

        # ------------------------------------------------------------
        # Name
        # ------------------------------------------------------------

        detailsSizer.Add(
            wx.StaticText(
                nebulaParent,
                label="Name:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nebulaName = wx.TextCtrl(
            nebulaParent
        )

        detailsSizer.Add(
            self.nebulaName,
            1,
            wx.EXPAND,
        )

        # ------------------------------------------------------------
        # Style
        # ------------------------------------------------------------

        detailsSizer.Add(
            wx.StaticText(
                nebulaParent,
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
            nebulaParent,
            choices=[
                "Cloud",
                "Outline",
                "Haze",
            ],
        )

        self.nebulaStyle.SetSelection(0)

        detailsSizer.Add(
            self.nebulaStyle,
            1,
            wx.EXPAND,
        )

        # ------------------------------------------------------------
        # Color
        # ------------------------------------------------------------

        detailsSizer.Add(
            wx.StaticText(
                nebulaParent,
                label="Color:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nebulaColor = wx.TextCtrl(
            nebulaParent
        )

        detailsSizer.Add(
            self.nebulaColor,
            1,
            wx.EXPAND,
        )

        # ------------------------------------------------------------
        # Opacity
        # ------------------------------------------------------------

        detailsSizer.Add(
            wx.StaticText(
                nebulaParent,
                label="Opacity:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nebulaOpacity = NumCtrl(
            nebulaParent,
            min=0.0,
            max=1.0,
            fractionWidth=2,
        )

        detailsSizer.Add(
            self.nebulaOpacity,
            1,
            wx.EXPAND,
        )

        nebulaSizer.Add(
            detailsSizer,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        # ------------------------------------------------------------
        # Points
        # ------------------------------------------------------------

        nebulaSizer.Add(
            wx.StaticText(
                nebulaParent,
                label="Points:",
            ),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            5,
        )

        self.nebulaPoints = wx.TextCtrl(
            nebulaParent,
            size=(-1, 100),
            style=wx.TE_MULTILINE,
        )

        nebulaSizer.Add(
            self.nebulaPoints,
            0,
            wx.LEFT | wx.RIGHT | wx.EXPAND,
            5,
        )

        pointHint = wx.StaticText(
            nebulaParent,
            label=(
                "Enter one boundary point per line as x,y. "
                "Points are connected in the entered order."
            ),
        )

        pointHint.Wrap(330)

        nebulaSizer.Add(
            pointHint,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        # ------------------------------------------------------------
        # Buttons
        # ------------------------------------------------------------

        buttonSizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        self.newNebulaButton = wx.Button(
            nebulaParent,
            label="New Nebula",
        )

        self.newNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.beginNewNebula,
        )

        self.newNebulaButton.Disable()

        buttonSizer.Add(
            self.newNebulaButton,
            0,
            wx.RIGHT,
            5,
        )

        self.deleteNebulaButton = wx.Button(
            nebulaParent,
            label="Delete Nebula",
        )

        self.deleteNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.deleteSelectedNebula,
        )

        self.deleteNebulaButton.Disable()

        buttonSizer.Add(
            self.deleteNebulaButton,
            0,
            wx.RIGHT,
            5,
        )

        self.cancelNebulaButton = wx.Button(
            nebulaParent,
            label="Cancel",
        )

        self.cancelNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.cancelNewNebula,
        )

        self.cancelNebulaButton.Disable()

        buttonSizer.Add(
            self.cancelNebulaButton,
            0,
            wx.RIGHT,
            5,
        )

        self.applyNebulaButton = wx.Button(
            nebulaParent,
            label="Apply Changes",
        )

        self.applyNebulaButton.Bind(
            wx.EVT_BUTTON,
            self.applyNebulaChanges,
        )

        self.applyNebulaButton.Disable()

        buttonSizer.Add(
            self.applyNebulaButton,
            0,
        )

        nebulaSizer.Add(
            buttonSizer,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
        )

        self.clearNebulaDetails()

    def refreshNebulaEditor(
            self,
            selectedIndex=0,
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
            selectedIndex = max(
                0,
                min(
                    selectedIndex,
                    len(self.nebulaList) - 1,
                ),
            )

            self.nebulaListControl.SetSelection(
                selectedIndex
            )

            self.showNebulaDetails(
                selectedIndex
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

        currentSelection = (
            self.nebulaListControl.GetSelection()
        )

        if currentSelection != wx.NOT_FOUND:
            self.nebulaListControl.Deselect(
                currentSelection
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

        existingNames = {
            nebula.name.casefold()
            for nebula in self.nebulaList
        }

        baseName = "Nebula"

        if baseName.casefold() not in existingNames:
            return baseName

        number = 2

        while (
                f"{baseName} {number}".casefold()
                in existingNames
        ):
            number += 1

        return f"{baseName} {number}"

    def cancelNewNebula(self, event):
        """Cancel creation of a nebula."""

        returnIndex = (
            self.nebulaCreationReturnIndex
        )

        self.leaveNebulaCreateMode()

        if self.nebulaList:
            if (
                    returnIndex == wx.NOT_FOUND
                    or returnIndex >= len(self.nebulaList)
            ):
                returnIndex = 0

            self.nebulaListControl.SetSelection(
                returnIndex
            )

            self.showNebulaDetails(
                returnIndex
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
            selectedIndex,
    ):
        """Validate and return the nebula editor values."""

        name = self.validateNebulaName(
            self.nebulaName.GetValue(),
            selectedIndex,
        )

        styleSelection = (
            self.nebulaStyle.GetSelection()
        )

        if styleSelection == wx.NOT_FOUND:
            raise ValueError(
                "Select a nebula style."
            )

        style = self.nebulaStyleValues[
            styleSelection
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
            selectedIndex=wx.NOT_FOUND,
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
                    index != selectedIndex
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

        for lineNumber, rawLine in enumerate(
                lines,
                start=1,
        ):
            line = rawLine.strip()

            if not line:
                continue

            match = re.fullmatch(
                r"\(?\s*(-?\d+)\s*,\s*(-?\d+)\s*\)?",
                line,
            )

            if match is None:
                raise ValueError(
                    "Invalid nebula point on line "
                    f"{lineNumber}: {rawLine}\n\n"
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

        nebula.normalize()

        self.nebulaList.append(
            nebula
        )

        newIndex = (
                len(self.nebulaList) - 1
        )

        self.leaveNebulaCreateMode()
        self.saveAndRedrawCurrentMap()
        self.refreshNebulaEditor(
            newIndex
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
            nextIndex = min(
                index,
                len(self.nebulaList) - 1,
            )

            self.refreshNebulaEditor(
                nextIndex
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

    def generateMap(self, event):
        """Generate a new random star map."""

        params = self.createParamDict()

        if not params["datafile"]:
            wx.MessageBox(
                "Enter a data filename before generating the map.",
                "Missing Data Filename",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        if not params["filename"]:
            wx.MessageBox(
                "Enter an output map filename before generating the map.",
                "Missing Map Filename",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        # Start generated names at S000 for each new map.
        StarSystem.id = 0

        starList = createSystems(params)
        jumpList = findJumps(starList)

        self.systemEditor.resetState()

        self.params = params
        self.starList = starList
        self.jumpList = jumpList
        self.nebulaList = []

        self.renderCurrentMap()
        self.saveCurrentMap()
        self.drawMap(self.params["filename"])
        self.refreshSystemEditor()
        self.refreshNebulaEditor()
        self.refreshExportControls()
        self.refreshMapBounds()

        self.SetStatusText(
            f"{len(self.starList)} star systems were randomly generated."
        )

    def renderCurrentMap(self):
        """Create the SVG from the current in-memory map state."""

        multipleList = findOverlaps(self.starList)
        definitionDictionary = {}

        symbolList = createMapSymbols(
            self.params,
            self.starList,
            multipleList,
            definitionDictionary,
        )

        # createMapSymbols sets drawnPos, which is required
        # by findConnections.
        connectionList = findConnections(
            self.starList,
            self.jumpList,
        )

        writeSvgMap(
            self.params,
            definitionDictionary,
            symbolList,
            connectionList,
            self.starList,
            self.nebulaList,
        )

    def saveCurrentMap(self):
        """Write the current state to the DAT file."""

        writeSystemData(
            self.params,
            self.starList,
        )

        writeFactionData(
            self.params,
            self.starList,
        )

        writePlanetData(
            self.params,
            self.starList,
        )

        writeConnectionData(
            self.params,
            self.jumpList,
        )

        writeNebulaData(
            self.params,
            self.nebulaList,
        )

    def saveAndRedrawCurrentMap(self):
        """Save the current data and refresh the SVG preview."""

        self.renderCurrentMap()
        self.saveCurrentMap()
        self.drawMap(self.params["filename"])
        self.refreshMapBounds()



    def hasCurrentMapBounds(self):
        """Return whether the current map has complete bounds."""

        requiredKeys = (
            "minX",
            "maxX",
            "minY",
            "maxY",
            "minZ",
            "maxZ",
        )

        return (
                bool(self.params)
                and all(
            key in self.params
            for key in requiredKeys
        )
        )





    def resetParameters(self, event):
        self.setDefaults()
        self.exportPngButton.Disable()
        self.SetStatusText(
            "Map parameters reset."
        )

    def setDefaults(self):
        self.xSize.SetValue(20)
        self.ySize.SetValue(20)
        self.zSize.SetValue(20)
        self.stellarDensity.SetValue(0.004)
        self.textScale.SetValue(1)
        self.outMapName.SetValue("sampleMap.svg")
        self.dataName.SetValue("sampleMap.dat")
        self.printZ.SetValue(True)

    def createParamDict(self):
        """Create parameters for generating a new random map."""

        params = {}

        # New randomly generated maps begin at X=1 and Y=1.
        params["minX"] = 1
        params["maxX"] = self.xSize.GetValue()

        params["minY"] = 1
        params["maxY"] = self.ySize.GetValue()

        zValue = self.zSize.GetValue() // 2

        params["minZ"] = -zValue
        params["maxZ"] = zValue

        if self.zSize.GetValue() % 2 == 0:
            params["minZ"] += 1

        params["stellarDensity"] = (
            self.stellarDensity.GetValue()
        )

        params["filename"] = (
            self.outMapName.GetValue().strip()
        )

        params["datafile"] = (
            self.dataName.GetValue().strip()
        )

        params["scale"] = (
            self.textScale.GetValue()
        )

        params["printZ"] = (
            self.printZ.GetValue()
        )

        return params

    def refreshMapBounds(self):
        """Display the current absolute map bounds."""

        requiredKeys = (
            "minX",
            "maxX",
            "minY",
            "maxY",
            "minZ",
            "maxZ",
        )

        hasMapBounds = (
                bool(self.params)
                and all(
            key in self.params
            for key in requiredKeys
        )
        )

        if not hasMapBounds:
            self.mapBoundsLabel.SetLabel(
                "No map loaded."
            )

            self.extendAmount.Disable()

            for button in self.mapBoundsButtons:
                button.Disable()

            self.refreshInputPanelLayout()
            return

        width = (
                self.params["maxX"]
                - self.params["minX"]
                + 1
        )

        height = (
                self.params["maxY"]
                - self.params["minY"]
                + 1
        )

        depth = (
                self.params["maxZ"]
                - self.params["minZ"]
                + 1
        )

        self.mapBoundsLabel.SetLabel(
            f'X: {self.params["minX"]} to '
            f'{self.params["maxX"]} '
            f"({width} points)\n"
            f'Y: {self.params["minY"]} to '
            f'{self.params["maxY"]} '
            f"({height} points)\n"
            f'Z: {self.params["minZ"]} to '
            f'{self.params["maxZ"]} '
            f"({depth} levels)"
        )

        self.extendAmount.Enable()

        for button in self.mapBoundsButtons:
            button.Enable()

        self.refreshInputPanelLayout()

    def extendMap(self, direction):
        """Extend the current map in one direction."""

        directionDefinitions = {
            "x-": ("minX", -1, "negative X"),
            "x+": ("maxX", 1, "positive X"),
            "y-": ("minY", -1, "negative Y"),
            "y+": ("maxY", 1, "positive Y"),
            "z-": ("minZ", -1, "negative Z"),
            "z+": ("maxZ", 1, "positive Z"),
        }

        if direction not in directionDefinitions:
            return

        if not self.hasCurrentMapBounds():
            wx.MessageBox(
                "Generate or load a map before extending it.",
                "No Map Available",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        amount = self.extendAmount.GetValue()

        if amount < 1:
            wx.MessageBox(
                "The extension amount must be at least 1.",
                "Invalid Extension Amount",
                wx.OK | wx.ICON_ERROR,
            )
            return

        parameterName, factor, label = (
            directionDefinitions[direction]
        )

        # This updates the actual map model.
        self.params[parameterName] += (
                factor * amount
        )

        self.saveAndRedrawCurrentMap()

        self.SetStatusText(
            f"Map extended by {amount} "
            f"unit(s) towards {label}."
        )

    def drawMap(self, file):
        self.mapPanel.setMap(file)
        self.mainSizer.Layout()
        self.Update()
        self.Refresh()

    def onResize(self, event):
        self.Update()
        self.Refresh()
        event.Skip()


    def loadMap(self, event):
        """Load an existing star map from the configured DAT file."""

        params = self.createParamDict()
        dataFilename = params["datafile"]

        if not dataFilename:
            wx.MessageBox(
                "Enter the DAT file that should be loaded.",
                "Missing Data Filename",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        if not params["filename"]:
            wx.MessageBox(
                "Enter an output map filename for the generated SVG.",
                "Missing Map Filename",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        loadedStarList = []
        loadedJumpList = []
        loadedNebulaList = []

        try:
            loadData(
                dataFilename,
                params,
                loadedStarList,
                loadedJumpList,
                loadedNebulaList

            )
        except (OSError, ValueError) as error:
            wx.MessageBox(
                str(error),
                "Unable to Load Map",
                wx.OK | wx.ICON_ERROR,
            )
            return

        self.systemEditor.resetState()

        self.params = params
        self.starList = loadedStarList
        self.jumpList = loadedJumpList
        self.nebulaList = loadedNebulaList

        self.renderCurrentMap()
        self.drawMap(self.params["filename"])
        self.refreshSystemEditor()
        self.refreshNebulaEditor()
        self.refreshExportControls()
        self.refreshMapBounds()

        self.SetStatusText(
            f"{len(self.starList)} star systems were loaded "
            f'from "{dataFilename}".'
        )

    def onExportPng(self, event):
        """Export the current SVG map to PNG in a background thread."""

        if not self.params:
            return

        svgFile = self.params.get(
            "filename"
        )

        if not svgFile:
            return

        self.exportPngButton.Disable()

        self.SetStatusText(
            "Exporting PNG..."
        )

        thread = threading.Thread(
            target=self.exportPngWorker,
            args=(svgFile,),
            daemon=True,
        )

        thread.start()

    def exportPngWorker(
            self,
            svgFile,
    ):
        """Run the PNG conversion outside the UI thread."""

        try:
            pngFile = exportPng(
                svgFile,
                scale=4.0,
            )

        except Exception as error:
            wx.CallAfter(
                self.finishPngExport,
                None,
                error,
            )

            return

        wx.CallAfter(
            self.finishPngExport,
            pngFile,
            None,
        )

    def finishPngExport(
            self,
            pngFile,
            error,
    ):
        """Update the UI after PNG export."""

        self.exportPngButton.Enable(
            bool(self.params)
        )

        if error is not None:
            self.SetStatusText(
                "PNG export failed."
            )

            wx.MessageBox(
                str(error),
                "PNG Export Error",
                wx.OK | wx.ICON_ERROR,
                self,
            )

            return

        self.SetStatusText(
            f"PNG exported: {pngFile}"
        )

    def refreshExportControls(self):
        """Enable export controls when a map exists."""

        self.exportPngButton.Enable(
            bool(self.params)
        )

    def refreshSystemEditor(
            self,
            selectedIndex=0,
    ):
        self.systemEditor.refreshSystemEditor(
            selectedIndex
        )

    def clearSystemDetails(self):
        self.systemEditor.clearSystemDetails()
