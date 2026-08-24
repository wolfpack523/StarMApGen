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
from exportPng import exportPng
from JumpLinkDialog import (
    JUMP_STATUS_OPTIONS,
)
from SystemEditorPanel import (
    SystemEditorPanel,
)
from NebulaEditorPanel import (
    NebulaEditorPanel,
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

        (
            self.nebulaPane,
            nebulaParent,
            nebulaSizer,
        ) = self.createCollapsibleSection(
            self.inputPanel,
            inputSizer,
            "Nebulae",
            expanded=False,
        )

        self.nebulaEditor = (
            NebulaEditorPanel(
                nebulaParent,
                self,
            )
        )

        nebulaSizer.Add(
            self.nebulaEditor,
            1,
            wx.EXPAND,
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

    def refreshNebulaEditor(
            self,
            selectedIndex=0,
    ):
        self.nebulaEditor.refreshNebulaEditor(
            selectedIndex
        )

    def clearNebulaDetails(self):
        self.nebulaEditor.clearNebulaDetails()