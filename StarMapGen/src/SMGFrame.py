import threading

import wx
import wx.lib.scrolledpanel

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
from SystemEditorPanel import (
    SystemEditorPanel,
)
from NebulaEditorPanel import (
    NebulaEditorPanel,
)
from MapBoundsPanel import MapBoundsPanel
from MapParametersPanel import (
    MapParametersPanel,
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

        (
            self.mapFilesPane,
            filesParent,
            filesSizer,
        ) = self.createCollapsibleSection(
            self.inputPanel,
            inputSizer,
            "Map Files and Display",
            expanded=True,
        )

        self.mapParametersPanel = (
            MapParametersPanel(
                filesParent,
                self,
            )
        )
        
        filesSizer.Add(
            self.mapParametersPanel,
            1,
            wx.EXPAND,
        )

        (
            self.mapBoundsPane,
            boundsParent,
            boundsSizer,
        ) = self.createCollapsibleSection(
            self.inputPanel,
            inputSizer,
            "Map Bounds",
            expanded=False,
        )

        self.mapBoundsPanel = (
            MapBoundsPanel(
                boundsParent,
                self,
            )
        )

        boundsSizer.Add(
            self.mapBoundsPanel,
            1,
            wx.EXPAND,
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

    def onResize(self, event):
        self.Update()
        self.Refresh()
        event.Skip()


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
        self.refreshMapControls()

        self.SetStatusText(
            f"{len(self.starList)} star systems were randomly generated."
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

        self.systemEditor.resetState()

        self.params = params
        self.starList = loadedStarList
        self.jumpList = loadedJumpList
        self.nebulaList = loadedNebulaList

        self.renderCurrentMap()
        self.drawMap(self.params["filename"])
        self.refreshMapControls()

        self.SetStatusText(
            f"{len(self.starList)} star systems were loaded "
            f'from "{dataFilename}".'
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

    def drawMap(self, file):
        self.mapPanel.setMap(file)
        self.mainSizer.Layout()
        self.Update()
        self.Refresh()

    def onExportPng(self, event):
        """Export the current SVG map to PNG in a background thread."""

        if not self.params:
            return

        svgFile = self.params.get(
            "filename"
        )

        if not svgFile:
            return

        self.mapParametersPanel.setExportEnabled(
            False
        )

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

        self.mapParametersPanel.setExportEnabled(
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

    def createParamDict(self):
        return (
            self.mapParametersPanel
            .createParamDict()
        )

    def refreshMapControls(self):
        """Refresh all controls that depend on the current map."""

        self.refreshSystemEditor()
        self.refreshNebulaEditor()
        self.refreshExportControls()
        self.refreshMapBounds()

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

    def refreshMapBounds(self):
        self.mapBoundsPanel.refreshMapBoundsControls()

    def refreshExportControls(self):
        self.mapParametersPanel.refreshExportControls()
