import re
import random
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
from JumpLink import JumpLink
from Nebula import Nebula
from exportPng import exportPng
from Planet import Planet

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

JUMP_STATUS_LABELS = dict(
    JUMP_STATUS_OPTIONS
)


class JumpLinkDialog(wx.Dialog):
    def __init__(
            self,
            parent,
            targetNames,
            targetName=None,
            status=JumpLink.STATUS_NORMAL,
            title="Jump Link",
    ):
        super().__init__(
            parent,
            title=title,
        )

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        formSizer = wx.FlexGridSizer(
            cols=2,
            vgap=8,
            hgap=8,
        )

        formSizer.AddGrowableCol(1, 1)

        formSizer.Add(
            wx.StaticText(
                self,
                label="Target System:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.targetChoice = wx.Choice(
            self,
            choices=targetNames,
        )

        formSizer.Add(
            self.targetChoice,
            1,
            wx.EXPAND,
        )

        formSizer.Add(
            wx.StaticText(
                self,
                label="Route Status:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.statusValues = [
            value
            for value, label in JUMP_STATUS_OPTIONS
        ]

        self.statusChoice = wx.Choice(
            self,
            choices=[
                label
                for value, label in JUMP_STATUS_OPTIONS
            ],
        )

        formSizer.Add(
            self.statusChoice,
            1,
            wx.EXPAND,
        )

        mainSizer.Add(
            formSizer,
            1,
            wx.ALL | wx.EXPAND,
            12,
        )

        buttonSizer = self.CreateButtonSizer(
            wx.OK | wx.CANCEL
        )

        mainSizer.Add(
            buttonSizer,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
            12,
        )

        self.SetSizerAndFit(mainSizer)

        if targetName in targetNames:
            self.targetChoice.SetSelection(
                targetNames.index(targetName)
            )
        elif targetNames:
            self.targetChoice.SetSelection(0)

        if status in self.statusValues:
            self.statusChoice.SetSelection(
                self.statusValues.index(status)
            )
        else:
            self.statusChoice.SetSelection(0)

    def getTargetName(self):
        return self.targetChoice.GetStringSelection()

    def getStatus(self):
        selection = self.statusChoice.GetSelection()

        if selection == wx.NOT_FOUND:
            return JumpLink.STATUS_NORMAL

        return self.statusValues[selection]


class PlanetDialog(wx.Dialog):
    """Dialog for creating or editing a planet."""

    def __init__(
            self,
            parent,
            planet=None,
            title="Planet",
    ):
        super().__init__(
            parent,
            title=title,
        )

        mainSizer = wx.BoxSizer(
            wx.VERTICAL
        )

        formSizer = wx.FlexGridSizer(
            cols=2,
            vgap=8,
            hgap=8,
        )

        formSizer.AddGrowableCol(
            1,
            1,
        )

        formSizer.Add(
            wx.StaticText(
                self,
                label="Name:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.nameControl = wx.TextCtrl(
            self
        )

        formSizer.Add(
            self.nameControl,
            1,
            wx.EXPAND,
        )

        formSizer.Add(
            wx.StaticText(
                self,
                label="Type:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.typeValues = list(
            Planet.VALID_TYPES
        )

        self.typeChoice = wx.Choice(
            self,
            choices=[
                Planet.TYPE_LABELS[value]
                for value in self.typeValues
            ],
        )

        formSizer.Add(
            self.typeChoice,
            1,
            wx.EXPAND,
        )

        formSizer.Add(
            wx.StaticText(
                self,
                label="Classification:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.classificationChoice = wx.Choice(
            self,
            choices=list(
                Planet.CLASSIFICATIONS
            ),
        )

        formSizer.Add(
            self.classificationChoice,
            1,
            wx.EXPAND,
        )

        mainSizer.Add(
            formSizer,
            1,
            wx.ALL | wx.EXPAND,
            12,
        )

        buttonSizer = self.CreateButtonSizer(
            wx.OK | wx.CANCEL
        )

        mainSizer.Add(
            buttonSizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            12,
        )

        self.SetSizerAndFit(
            mainSizer
        )

        if planet is not None:
            self.nameControl.SetValue(
                planet.name
            )

            if planet.planetType in self.typeValues:
                self.typeChoice.SetSelection(
                    self.typeValues.index(
                        planet.planetType
                    )
                )

            if (
                    planet.classification
                    in Planet.CLASSIFICATIONS
            ):
                self.classificationChoice.SetSelection(
                    Planet.CLASSIFICATIONS.index(
                        planet.classification
                    )
                )
            else:
                self.classificationChoice.SetStringSelection(
                    Planet.DEFAULT_CLASSIFICATION
                )

        else:
            self.typeChoice.SetSelection(0)

            self.classificationChoice.SetStringSelection(
                Planet.DEFAULT_CLASSIFICATION
            )

        self.nameControl.SetFocus()

    def getPlanetName(self):
        return (
            self.nameControl
            .GetValue()
            .strip()
        )

    def getPlanetType(self):
        selection = (
            self.typeChoice
            .GetSelection()
        )

        if selection == wx.NOT_FOUND:
            return Planet.TYPE_OTHER

        return self.typeValues[
            selection
        ]

    def getClassification(self):
        selection = (
            self.classificationChoice
            .GetSelection()
        )

        if selection == wx.NOT_FOUND:
            return Planet.DEFAULT_CLASSIFICATION

        return Planet.CLASSIFICATIONS[
            selection
        ]


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
        self.editedPlanets = []
        self.jumpList = []
        self.nebulaList = []

        # Editor state
        self.selectedSystemIndex = wx.NOT_FOUND
        self.isCreatingSystem = False
        self.creationReturnIndex = wx.NOT_FOUND

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

        self.createSystemEditor(
            self.inputPanel,
            inputSizer,
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

    def createSystemEditor(self, parent, inputSizer):
        """Create the star system and jump link editor."""

        editorSizer = wx.StaticBoxSizer(
            wx.VERTICAL,
            parent,
            label="Star Systems",
        )

        self.systemList = wx.ListBox(
            parent,
            size=(340, 140),
            style=wx.LB_SINGLE,
        )

        self.systemList.Bind(
            wx.EVT_LISTBOX,
            self.onSystemSelected,
        )

        editorSizer.Add(
            self.systemList,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        detailsSizer = wx.FlexGridSizer(
            cols=2,
            vgap=5,
            hgap=5,
        )

        detailsSizer.AddGrowableCol(1, 1)

        detailsSizer.Add(
            wx.StaticText(
                parent,
                label="Name:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemName = wx.TextCtrl(parent)

        detailsSizer.Add(
            self.systemName,
            1,
            wx.EXPAND,
        )

        detailsSizer.Add(
            wx.StaticText(
                parent,
                label="Faction:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemFaction = wx.TextCtrl(
            parent
        )

        detailsSizer.Add(
            self.systemFaction,
            1,
            wx.EXPAND,
        )

        detailsSizer.Add(
            wx.StaticText(
                parent,
                label="X:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemX = wx.TextCtrl(parent)

        detailsSizer.Add(
            self.systemX,
            1,
            wx.EXPAND,
        )

        detailsSizer.Add(
            wx.StaticText(
                parent,
                label="Y:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemY = wx.TextCtrl(parent)

        detailsSizer.Add(
            self.systemY,
            1,
            wx.EXPAND,
        )

        detailsSizer.Add(
            wx.StaticText(
                parent,
                label="Z:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemZ = wx.TextCtrl(parent)

        detailsSizer.Add(
            self.systemZ,
            1,
            wx.EXPAND,
        )

        detailsSizer.Add(
            wx.StaticText(
                parent,
                label="Number of Stars:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.systemStarCount = wx.TextCtrl(
            parent,
            style=wx.TE_READONLY,
        )

        detailsSizer.Add(
            self.systemStarCount,
            1,
            wx.EXPAND,
        )

        detailsSizer.Add(
            wx.StaticText(
                parent,
                label="Spectral Types:",
            ),
            0,
            wx.ALIGN_TOP,
        )

        self.systemSpectralTypes = wx.TextCtrl(
            parent,
            size=(-1, 55),
            style=wx.TE_MULTILINE,
        )

        detailsSizer.Add(
            self.systemSpectralTypes,
            1,
            wx.EXPAND,
        )

        editorSizer.Add(
            detailsSizer,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        spectralHelpSizer = wx.BoxSizer(wx.HORIZONTAL)

        spectralHint = wx.StaticText(
            parent,
            label=(
                "Separate spectral types with commas, "
                "semicolons, or new lines."
            ),
        )

        spectralHint.Wrap(240)

        spectralHelpSizer.Add(
            spectralHint,
            1,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.randomizeSpectralTypesButton = wx.Button(
            parent,
            label="Randomize",
        )

        self.randomizeSpectralTypesButton.Bind(
            wx.EVT_BUTTON,
            self.randomizeSpectralTypes,
        )

        self.randomizeSpectralTypesButton.Disable()

        spectralHelpSizer.Add(
            self.randomizeSpectralTypesButton,
            0,
            wx.LEFT,
            5,
        )

        spectralHelpButton = wx.Button(
            parent,
            label="Spectral Type Help",
        )

        spectralHelpButton.Bind(
            wx.EVT_BUTTON,
            self.showSpectralTypeHelp,
        )

        spectralHelpSizer.Add(
            spectralHelpButton,
            0,
            wx.LEFT,
            5,
        )

        editorSizer.Add(
            spectralHelpSizer,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
            5,
        )

        editorSizer.Add(
            wx.StaticText(
                parent,
                label="Planets:",
            ),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            5,
        )

        self.planetListControl = wx.ListCtrl(
            parent,
            size=(-1, 120),
            style=(
                    wx.LC_REPORT
                    | wx.LC_SINGLE_SEL
                    | wx.BORDER_SUNKEN
            ),
        )

        self.planetListControl.InsertColumn(
            0,
            "Planet",
            width=190,
        )

        self.planetListControl.InsertColumn(
            1,
            "Type",
            width=120,
        )

        self.planetListControl.InsertColumn(
            2,
            "Classification",
            width=160,
        )

        self.planetListControl.Bind(
            wx.EVT_LIST_ITEM_SELECTED,
            self.onPlanetSelectionChanged,
        )

        self.planetListControl.Bind(
            wx.EVT_LIST_ITEM_DESELECTED,
            self.onPlanetSelectionChanged,
        )

        self.planetListControl.Bind(
            wx.EVT_LIST_ITEM_ACTIVATED,
            self.editPlanet,
        )

        editorSizer.Add(
            self.planetListControl,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
        )

        planetButtonSizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        self.addPlanetButton = wx.Button(
            parent,
            label="Add Planet",
        )

        self.addPlanetButton.Bind(
            wx.EVT_BUTTON,
            self.addPlanet,
        )

        planetButtonSizer.Add(
            self.addPlanetButton,
            0,
            wx.RIGHT,
            5,
        )

        self.editPlanetButton = wx.Button(
            parent,
            label="Edit Planet",
        )

        self.editPlanetButton.Bind(
            wx.EVT_BUTTON,
            self.editPlanet,
        )

        self.editPlanetButton.Disable()

        planetButtonSizer.Add(
            self.editPlanetButton,
            0,
            wx.RIGHT,
            5,
        )

        self.removePlanetButton = wx.Button(
            parent,
            label="Remove Planet",
        )

        self.removePlanetButton.Bind(
            wx.EVT_BUTTON,
            self.removePlanet,
        )

        self.removePlanetButton.Disable()

        planetButtonSizer.Add(
            self.removePlanetButton,
            0,
        )

        editorSizer.Add(
            planetButtonSizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.ALIGN_RIGHT,
            5,
        )

        editorSizer.Add(
            wx.StaticText(
                parent,
                label="Jump Links:",
            ),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            5,
        )

        jumpHint = wx.StaticText(
            parent,
            label=(
                "Add, edit, or remove jump links and assign "
                "a route status to each connection."
            ),
        )

        jumpHint.Wrap(330)

        editorSizer.Add(
            jumpHint,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
            5,
        )

        self.displayedJumpLinks = []

        self.jumpListControl = wx.ListCtrl(
            parent,
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

        editorSizer.Add(
            self.jumpListControl,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
            5,
        )

        jumpButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.addJumpButton = wx.Button(
            parent,
            label="Add Link",
        )
        self.addJumpButton.Bind(
            wx.EVT_BUTTON,
            self.addJumpLink,
        )
        self.addJumpButton.Disable()

        jumpButtonSizer.Add(
            self.addJumpButton,
            0,
            wx.RIGHT,
            5,
        )

        self.editJumpButton = wx.Button(
            parent,
            label="Edit Link",
        )
        self.editJumpButton.Bind(
            wx.EVT_BUTTON,
            self.editJumpLink,
        )
        self.editJumpButton.Disable()

        jumpButtonSizer.Add(
            self.editJumpButton,
            0,
            wx.RIGHT,
            5,
        )

        self.removeJumpButton = wx.Button(
            parent,
            label="Remove Link",
        )
        self.removeJumpButton.Bind(
            wx.EVT_BUTTON,
            self.removeJumpLink,
        )
        self.removeJumpButton.Disable()

        jumpButtonSizer.Add(
            self.removeJumpButton,
            0,
        )

        editorSizer.Add(
            jumpButtonSizer,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT,
            5,
        )

        editorButtonSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.newSystemButton = wx.Button(
            parent,
            label="New System",
        )

        self.newSystemButton.Bind(
            wx.EVT_BUTTON,
            self.beginNewSystem,
        )

        self.newSystemButton.Disable()

        editorButtonSizer.Add(
            self.newSystemButton,
            0,
            wx.RIGHT,
            5,
        )

        self.deleteSystemButton = wx.Button(
            parent,
            label="Delete System",
        )

        self.deleteSystemButton.Bind(
            wx.EVT_BUTTON,
            self.deleteSelectedSystem,
        )

        self.deleteSystemButton.Disable()

        editorButtonSizer.Add(
            self.deleteSystemButton,
            0,
            wx.RIGHT,
            5,
        )

        self.cancelSystemButton = wx.Button(
            parent,
            label="Cancel",
        )

        self.cancelSystemButton.Bind(
            wx.EVT_BUTTON,
            self.cancelNewSystem,
        )

        self.cancelSystemButton.Disable()

        editorButtonSizer.Add(
            self.cancelSystemButton,
            0,
            wx.RIGHT,
            5,
        )

        self.applySystemButton = wx.Button(
            parent,
            label="Apply Changes",
        )

        self.applySystemButton.Bind(
            wx.EVT_BUTTON,
            self.applySystemChanges,
        )

        self.applySystemButton.Disable()

        editorButtonSizer.Add(
            self.applySystemButton,
            0,
        )

        editorSizer.Add(
            editorButtonSizer,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
        )

        inputSizer.Add(
            editorSizer,
            0,
            wx.TOP | wx.EXPAND,
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

        self.isCreatingSystem = False
        self.creationReturnIndex = wx.NOT_FOUND

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

    def refreshSystemEditor(self, selectedIndex=0):
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
            selectedIndex = max(
                0,
                min(
                    selectedIndex,
                    len(self.starList) - 1,
                ),
            )

            self.systemList.SetSelection(selectedIndex)
            self.showSystemDetails(selectedIndex)
        else:
            self.clearSystemDetails()

        self.mainSizer.Layout()

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

        self.editedPlanets = [
            Planet(
                name=planet.name,
                planetType=planet.planetType,
                classification=planet.classification,
            )
            for planet in system.planets
        ]

        self.refreshPlanetEditor()

        self.randomizeSpectralTypesButton.Enable()

        self.refreshJumpEditor(system.name)

        self.applySystemButton.SetLabel(
            "Apply Changes"
        )
        self.applySystemButton.Enable()
        self.deleteSystemButton.Enable()
        self.addPlanetButton.Enable()

    def refreshJumpEditor(self, systemName):
        """Display the jump links belonging to one system."""

        self.displayedJumpLinks = []
        self.jumpListControl.DeleteAllItems()

        if systemName is None:
            self.jumpListControl.Disable()
            self.updateJumpButtons()
            return

        displayedLinks = []

        for jump in self.jumpList:
            if not jump.contains(systemName):
                continue

            otherName = jump.getOtherSystemName(
                systemName
            )

            if otherName is None:
                continue

            displayedLinks.append(
                (
                    otherName,
                    jump,
                )
            )

        displayedLinks.sort(
            key=lambda item: item[0].casefold()
        )

        for otherName, jump in displayedLinks:
            row = self.jumpListControl.InsertItem(
                self.jumpListControl.GetItemCount(),
                otherName,
            )

            self.jumpListControl.SetItem(
                row,
                1,
                JUMP_STATUS_LABELS.get(
                    jump.status,
                    jump.status,
                ),
            )

            self.displayedJumpLinks.append(jump)

        self.jumpListControl.Enable()
        self.updateJumpButtons()

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

        currentSelection = self.systemList.GetSelection()

        if currentSelection != wx.NOT_FOUND:
            self.systemList.Deselect(currentSelection)

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

        self.editedPlanets = []

        self.refreshPlanetEditor()
        self.addPlanetButton.Enable()

        # A new system may be linked to any existing system.
        self.refreshJumpEditor(None)

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

        currentValue = (
            self.systemSpectralTypes
            .GetValue()
        )

        currentTypes = [
            item
            for item in re.split(
                r"[,;\r\n]+",
                currentValue,
            )
            if item.strip()
        ]

        starCount = max(
            1,
            len(currentTypes),
        )

        spectralTypes = [
            self.createRandomSpectralType()
            for _ in range(starCount)
        ]

        self.systemSpectralTypes.SetValue(
            ", ".join(spectralTypes)
        )

        self.systemStarCount.SetValue(
            str(starCount)
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

        returnIndex = self.creationReturnIndex

        self.leaveCreateMode()

        if self.starList:
            if (
                    returnIndex == wx.NOT_FOUND
                    or returnIndex >= len(self.starList)
            ):
                returnIndex = 0

            self.systemList.SetSelection(returnIndex)
            self.showSystemDetails(returnIndex)
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

        existingNames = {
            system.name.casefold()
            for system in self.starList
        }

        highestNumber = -1

        for system in self.starList:
            match = re.fullmatch(
                r"S(\d+)",
                system.name.strip(),
                re.IGNORECASE,
            )

            if match is None:
                continue

            highestNumber = max(
                highestNumber,
                int(match.group(1)),
            )

        nextNumber = highestNumber + 1

        while (
                f"S{nextNumber:03d}".casefold()
                in existingNames
        ):
            nextNumber += 1

        return f"S{nextNumber:03d}"

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

        newIndex = len(self.starList) - 1

        self.leaveCreateMode()
        self.saveAndRedrawCurrentMap()
        self.refreshSystemEditor(newIndex)

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
        oldName = system.name

        self.applyValuesToSystem(
            system,
            values,
        )

        if oldName != system.name:
            for jump in self.jumpList:
                jump.renameSystem(
                    oldName,
                    system.name,
                )

        self.saveAndRedrawCurrentMap()
        self.refreshSystemEditor(index)

        self.SetStatusText(
            f'Changes to "{system.name}" were saved.'
        )

    def readSystemEditorValues(self, selectedIndex):
        """Validate and return all editable values."""

        if not self.hasCurrentMapBounds():
            raise ValueError(
                "No valid map bounds are available."
            )

        name = self.validateSystemName(
            self.systemName.GetValue(),
            selectedIndex,
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

        spectralTypes = self.parseSpectralTypes(
            self.systemSpectralTypes.GetValue()
        )

        return {
            "name": name,
            "faction": faction,
            "x": x,
            "y": y,
            "z": z,
            "stars": spectralTypes,
            "planets": [
                Planet(
                    name=planet.name,
                    planetType=planet.planetType,
                    classification=planet.classification,
                )
                for planet in self.editedPlanets
            ],
        }

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
            selectedIndex=wx.NOT_FOUND,
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
                    index != selectedIndex
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

        spectralTypes = [
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

        if not spectralTypes:
            raise ValueError(
                "A star system must contain at least one star."
            )

        if len(spectralTypes) > 10:
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

        invalidTypes = [
            spectralType
            for spectralType in spectralTypes
            if pattern.fullmatch(spectralType) is None
        ]

        if invalidTypes:
            invalidText = ", ".join(invalidTypes)

            raise ValueError(
                "Unsupported spectral type(s): "
                f"{invalidText}.\n\n"
                "Use values such as G2, M4, K0III, M2I, "
                "BD, WD, NS, or BH."
            )

        return spectralTypes

    def showValidationError(self, error):
        """Display a validation error."""

        wx.MessageBox(
            str(error),
            "Invalid star system data",
            wx.OK | wx.ICON_ERROR,
        )

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

        self.displayedJumpLinks = []
        self.jumpListControl.DeleteAllItems()
        self.jumpListControl.Disable()

        self.addJumpButton.Disable()
        self.editJumpButton.Disable()
        self.removeJumpButton.Disable()
        self.editedPlanets = []

        self.planetListControl.DeleteAllItems()
        self.addPlanetButton.Disable()
        self.editPlanetButton.Disable()
        self.removePlanetButton.Disable()

        self.cancelSystemButton.Disable()
        self.applySystemButton.Disable()
        self.cancelSystemButton.Disable()

        self.newSystemButton.Enable(bool(self.params))

    def showSpectralTypeHelp(self, event):
        """Show an explanation of the supported spectral types."""

        helpText = """SPECTRAL CLASSES

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

        dialogSizer = wx.BoxSizer(wx.VERTICAL)

        helpField = wx.TextCtrl(
            dialog,
            value=helpText,
            style=(
                    wx.TE_MULTILINE
                    | wx.TE_READONLY
                    | wx.TE_RICH2
            ),
        )

        dialogSizer.Add(
            helpField,
            1,
            wx.ALL | wx.EXPAND,
            10,
        )

        closeButton = wx.Button(
            dialog,
            wx.ID_OK,
            label="Close",
        )

        dialogSizer.Add(
            closeButton,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.ALIGN_RIGHT,
            10,
        )

        dialog.SetSizer(dialogSizer)

        try:
            dialog.ShowModal()
        finally:
            dialog.Destroy()

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

    def onJumpSelectionChanged(self, event):
        self.updateJumpButtons()
        event.Skip()

    def updateJumpButtons(self):
        systemName = self.getCurrentSystemName()

        canEdit = (
                systemName is not None
                and self.getSelectedJumpLink() is not None
                and not self.isCreatingSystem
        )

        canAdd = (
                systemName is not None
                and bool(self.getAvailableJumpTargets())
                and not self.isCreatingSystem
        )

        self.addJumpButton.Enable(canAdd)
        self.editJumpButton.Enable(canEdit)
        self.removeJumpButton.Enable(canEdit)

    def getCurrentSystemName(self):
        if self.isCreatingSystem:
            return None

        index = self.selectedSystemIndex

        if (
                index == wx.NOT_FOUND
                or not 0 <= index < len(self.starList)
        ):
            return None

        return self.starList[index].name

    def getSelectedJumpLink(self):
        selectedRow = (
            self.jumpListControl.GetFirstSelected()
        )

        if (
                selectedRow == -1
                or not 0 <= selectedRow < len(
            self.displayedJumpLinks
        )
        ):
            return None

        return self.displayedJumpLinks[selectedRow]

    def getAvailableJumpTargets(
            self,
            currentTarget=None,
    ):
        systemName = self.getCurrentSystemName()

        if systemName is None:
            return []

        connectedNames = {
            jump.getOtherSystemName(systemName)
            for jump in self.jumpList
            if jump.contains(systemName)
        }

        return sorted(
            [
                system.name
                for system in self.starList
                if (
                    system.name != systemName
                    and (
                            system.name == currentTarget
                            or system.name not in connectedNames
                    )
            )
            ],
            key=str.casefold,
        )

    def addJumpLink(self, event):
        systemName = self.getCurrentSystemName()

        if systemName is None:
            return

        targetNames = self.getAvailableJumpTargets()

        if not targetNames:
            wx.MessageBox(
                "There are no unconnected star systems.",
                "Add Jump Link",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        dialog = JumpLinkDialog(
            self,
            targetNames,
            title="Add Jump Link",
        )

        try:
            if dialog.ShowModal() != wx.ID_OK:
                return

            targetName = dialog.getTargetName()
            status = dialog.getStatus()
        finally:
            dialog.Destroy()

        self.jumpList.append(
            JumpLink(
                systemName,
                targetName,
                status,
            )
        )

        self.saveAndRedrawCurrentMap()
        self.refreshJumpEditor(systemName)

        self.SetStatusText(
            f'Jump link to "{targetName}" was added.'
        )

    def editJumpLink(self, event):
        systemName = self.getCurrentSystemName()
        jump = self.getSelectedJumpLink()

        if systemName is None or jump is None:
            return

        currentTarget = jump.getOtherSystemName(
            systemName
        )

        targetNames = self.getAvailableJumpTargets(
            currentTarget,
        )

        dialog = JumpLinkDialog(
            self,
            targetNames,
            targetName=currentTarget,
            status=jump.status,
            title="Edit Jump Link",
        )

        try:
            if dialog.ShowModal() != wx.ID_OK:
                return

            targetName = dialog.getTargetName()
            status = dialog.getStatus()
        finally:
            dialog.Destroy()

        jump.startName = systemName
        jump.endName = targetName
        jump.status = status

        self.saveAndRedrawCurrentMap()
        self.refreshJumpEditor(systemName)

        self.SetStatusText(
            f'Jump link to "{targetName}" was updated.'
        )

    def removeJumpLink(self, event):
        systemName = self.getCurrentSystemName()
        jump = self.getSelectedJumpLink()

        if systemName is None or jump is None:
            return

        targetName = jump.getOtherSystemName(
            systemName
        )

        result = wx.MessageBox(
            f'Remove the jump link to "{targetName}"?',
            "Remove Jump Link",
            wx.YES_NO
            | wx.NO_DEFAULT
            | wx.ICON_QUESTION,
        )

        if result != wx.YES:
            return

        self.jumpList.remove(jump)

        self.saveAndRedrawCurrentMap()
        self.refreshJumpEditor(systemName)

        self.SetStatusText(
            f'Jump link to "{targetName}" was removed.'
        )

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

        connectedLinks = [
            jump
            for jump in self.jumpList
            if jump.contains(system.name)
        ]

        message = (
            f'Delete the star system "{system.name}"?'
        )

        if connectedLinks:
            linkWord = (
                "jump link"
                if len(connectedLinks) == 1
                else "jump links"
            )

            message += (
                f"\n\n{len(connectedLinks)} {linkWord} "
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

        deletedName = system.name

        # Remove every jump link involving the deleted system.
        self.jumpList = [
            jump
            for jump in self.jumpList
            if not jump.contains(deletedName)
        ]

        # Remove the actual star system.
        del self.starList[index]

        self.selectedSystemIndex = wx.NOT_FOUND

        self.saveAndRedrawCurrentMap()

        if self.starList:
            # Select the next system. If the deleted system was the
            # final entry, select the new final entry instead.
            nextIndex = min(
                index,
                len(self.starList) - 1,
            )

            self.refreshSystemEditor(nextIndex)
        else:
            self.refreshSystemEditor()

        self.SetStatusText(
            f'Star system "{deletedName}" and '
            f"{len(connectedLinks)} connected jump link(s) "
            "were deleted."
        )

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

        self.isCreatingSystem = False
        self.creationReturnIndex = wx.NOT_FOUND

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

    def refreshPlanetEditor(self):
        """Refresh the temporary planet list."""

        self.planetListControl.DeleteAllItems()

        for planet in self.editedPlanets:
            row = self.planetListControl.InsertItem(
                self.planetListControl.GetItemCount(),
                planet.name,
            )

            self.planetListControl.SetItem(
                row,
                1,
                planet.getTypeLabel(),
            )

            self.planetListControl.SetItem(
                row,
                2,
                planet.classification,
            )

        self.updatePlanetButtons()

    def onPlanetSelectionChanged(
            self,
            event,
    ):
        """Update planet buttons after selecting a row."""

        self.updatePlanetButtons()

        event.Skip()

    def updatePlanetButtons(self):
        """Enable planet actions according to the selection."""

        selectedIndex = (
            self.planetListControl
            .GetFirstSelected()
        )

        hasSelection = (
                selectedIndex != -1
        )

        self.editPlanetButton.Enable(
            hasSelection
        )

        self.removePlanetButton.Enable(
            hasSelection
        )

    def validatePlanetName(
            self,
            name,
            ignoredIndex=-1,
    ):
        """Validate a planet name inside the current system."""

        name = name.strip()

        if not name:
            raise ValueError(
                "The planet name must not be empty."
            )

        if '"' in name:
            raise ValueError(
                'The planet name must not contain a double quote (").'
            )

        for index, planet in enumerate(
                self.editedPlanets
        ):
            if (
                    index != ignoredIndex
                    and planet.name.casefold()
                    == name.casefold()
            ):
                raise ValueError(
                    f'A planet named "{name}" already exists '
                    "in this system."
                )

        return name

    def addPlanet(self, event):
        """Add a planet to the current editor state."""

        dialog = PlanetDialog(
            self,
            title="Add Planet",
        )

        try:
            if dialog.ShowModal() != wx.ID_OK:
                return

            try:
                name = self.validatePlanetName(
                    dialog.getPlanetName()
                )
            except ValueError as error:
                wx.MessageBox(
                    str(error),
                    "Invalid Planet",
                    wx.OK | wx.ICON_ERROR,
                    self,
                )
                return

            self.editedPlanets.append(
                Planet(
                    name=name,
                    planetType=dialog.getPlanetType(),
                    classification=dialog.getClassification(),
                )
            )

            self.applySystemButton.Enable()

            self.SetStatusText(
                "Planet list changed. Use Apply Changes to save."
            )

            self.refreshPlanetEditor()

        finally:
            dialog.Destroy()

    def editPlanet(self, event):
        """Edit the selected planet."""

        index = (
            self.planetListControl
            .GetFirstSelected()
        )

        if index == -1:
            return

        planet = self.editedPlanets[index]

        dialog = PlanetDialog(
            self,
            planet=planet,
            title="Edit Planet",
        )

        try:
            if dialog.ShowModal() != wx.ID_OK:
                return

            try:
                name = self.validatePlanetName(
                    dialog.getPlanetName(),
                    ignoredIndex=index,
                )
            except ValueError as error:
                wx.MessageBox(
                    str(error),
                    "Invalid Planet",
                    wx.OK | wx.ICON_ERROR,
                    self,
                )
                return

            planet.name = name
            planet.planetType = (
                dialog.getPlanetType()
            )

            planet.classification = (
                dialog.getClassification()
            )

            self.applySystemButton.Enable()

            self.SetStatusText(
                "Planet list changed. Use Apply Changes to save."
            )

            self.planetListControl.Select(
                index
            )
            self.refreshPlanetEditor()

        finally:
            dialog.Destroy()

    def removePlanet(self, event):
        """Remove the selected planet from the editor."""

        index = (
            self.planetListControl
            .GetFirstSelected()
        )

        if index == -1:
            return

        del self.editedPlanets[index]

        self.applySystemButton.Enable()

        self.SetStatusText(
            "Planet list changed. Use Apply Changes to save."
        )

        self.refreshPlanetEditor()
