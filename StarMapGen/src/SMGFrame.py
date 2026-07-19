import re

import wx
import wx.lib.intctrl
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
from writeData import writeConnectionData, writeSystemData


class SMGFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Star Map Generator")
        self.CreateStatusBar()

        # Current map state. These values remain available for the complete
        # lifetime of the application and can later be edited by the UI.
        self.params = {}
        self.starList = []
        self.jumpList = []
        self.selectedSystemIndex = wx.NOT_FOUND

        self.Center()

        mainPanel = wx.Panel(self)

        # Sizer for entire window
        self.mainSizer = wx.BoxSizer()

        # Sizer for left half of window
        inputSizer = wx.BoxSizer(wx.VERTICAL)

        # Sizer for the input data parameters
        dataSizer = wx.StaticBoxSizer(
            wx.VERTICAL,
            mainPanel,
            label="Map Parameters",
        )

        # X dimension
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        xSizeLabel = wx.StaticText(mainPanel, label="Map Width (x):")
        sizer1.Add(xSizeLabel, 0, wx.TOP, 10)
        self.xSize = wx.lib.intctrl.IntCtrl(mainPanel, min=1)
        sizer1.Add(self.xSize, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer1, 0, wx.ALIGN_RIGHT)

        # Y dimension
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        ySizeLabel = wx.StaticText(mainPanel, label="Map Height (y):")
        sizer2.Add(ySizeLabel, 0, wx.TOP, 10)
        self.ySize = wx.lib.intctrl.IntCtrl(mainPanel, min=1)
        sizer2.Add(self.ySize, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer2, 0, wx.ALIGN_RIGHT)

        # Z dimension
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        zSizeLabel = wx.StaticText(mainPanel, label="Map Thickness (z):")
        sizer3.Add(zSizeLabel, 0, wx.TOP, 10)
        self.zSize = wx.lib.intctrl.IntCtrl(mainPanel, min=1)
        sizer3.Add(self.zSize, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer3, 0, wx.ALIGN_RIGHT)

        # Stellar density
        sizer4 = wx.BoxSizer(wx.HORIZONTAL)
        densityLabel = wx.StaticText(mainPanel, label="Stellar Density:")
        sizer4.Add(densityLabel, 0, wx.TOP, 10)
        self.stellarDensity = NumCtrl(mainPanel, min=0, fractionWidth=4)
        sizer4.Add(self.stellarDensity, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer4, 0, wx.ALIGN_RIGHT)

        # Text scale
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        textScaleLabel = wx.StaticText(mainPanel, label="Text Scale:")
        sizer5.Add(textScaleLabel, 0, wx.TOP, 10)
        self.textScale = NumCtrl(mainPanel, min=0.25, fractionWidth=2)
        sizer5.Add(self.textScale, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer5, 0, wx.ALIGN_RIGHT)

        # Output map filename
        sizer6 = wx.BoxSizer(wx.HORIZONTAL)
        outMapNameLabel = wx.StaticText(
            mainPanel,
            label="Output Map Filename:",
        )
        sizer6.Add(outMapNameLabel, 0, wx.TOP, 10)
        self.outMapName = wx.TextCtrl(mainPanel)
        sizer6.Add(self.outMapName, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer6, 0, wx.ALIGN_RIGHT)

        # Output data filename
        sizer7 = wx.BoxSizer(wx.HORIZONTAL)
        outDataNameLabel = wx.StaticText(
            mainPanel,
            label="Output Data Filename:",
        )
        sizer7.Add(outDataNameLabel, 0, wx.TOP, 10)
        self.outDataName = wx.TextCtrl(mainPanel)
        sizer7.Add(self.outDataName, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer7, 0, wx.ALIGN_RIGHT)

        # Input data filename
        sizer8 = wx.BoxSizer(wx.HORIZONTAL)
        inDataNameLabel = wx.StaticText(
            mainPanel,
            label="Input Data Filename:",
        )
        sizer8.Add(inDataNameLabel, 0, wx.TOP, 10)
        self.inDataName = wx.TextCtrl(mainPanel)
        sizer8.Add(self.inDataName, 0, wx.ALL | wx.EXPAND, 5)
        dataSizer.Add(sizer8, 0, wx.ALIGN_RIGHT)

        # Print Z coordinate
        sizer9 = wx.BoxSizer(wx.HORIZONTAL)
        printZLabel = wx.StaticText(mainPanel, label="Print Z coordinate:")
        sizer9.Add(printZLabel, 0, wx.TOP, 5)
        self.printZ = wx.CheckBox(mainPanel)
        sizer9.Add(self.printZ, 0, wx.ALL, 5)
        dataSizer.Add(sizer9, 0, wx.ALIGN_RIGHT)

        inputSizer.Add(dataSizer, 0)

        # Buttons
        btnSizer = wx.BoxSizer()

        generateBtn = wx.Button(mainPanel, label="Generate Map")
        generateBtn.Bind(wx.EVT_BUTTON, self.generateMap)
        btnSizer.Add(generateBtn, 0, wx.ALL, 5)

        clearBtn = wx.Button(mainPanel, label="Reset Values")
        clearBtn.Bind(wx.EVT_BUTTON, self.resetParameters)
        btnSizer.Add(clearBtn, 0, wx.ALL, 5)

        inputSizer.Add(btnSizer, 0, wx.ALL | wx.CENTER, 5)

        # Star system list and details
        systemEditorSizer = wx.StaticBoxSizer(
            wx.VERTICAL,
            mainPanel,
            label="Star Systems",
        )

        self.systemList = wx.ListBox(
            mainPanel,
            size=(320, 160),
            style=wx.LB_SINGLE,
        )
        self.systemList.Bind(wx.EVT_LISTBOX, self.onSystemSelected)
        systemEditorSizer.Add(
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
            wx.StaticText(mainPanel, label="Name:"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        self.systemName = wx.TextCtrl(mainPanel)
        detailsSizer.Add(self.systemName, 1, wx.EXPAND)

        detailsSizer.Add(
            wx.StaticText(mainPanel, label="X:"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        self.systemX = wx.TextCtrl(mainPanel)
        detailsSizer.Add(self.systemX, 1, wx.EXPAND)

        detailsSizer.Add(
            wx.StaticText(mainPanel, label="Y:"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        self.systemY = wx.TextCtrl(mainPanel)
        detailsSizer.Add(self.systemY, 1, wx.EXPAND)

        detailsSizer.Add(
            wx.StaticText(mainPanel, label="Z:"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        self.systemZ = wx.TextCtrl(mainPanel)
        detailsSizer.Add(self.systemZ, 1, wx.EXPAND)

        detailsSizer.Add(
            wx.StaticText(mainPanel, label="Number of Stars:"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        self.systemStarCount = wx.TextCtrl(
            mainPanel,
            style=wx.TE_READONLY,
        )
        detailsSizer.Add(self.systemStarCount, 1, wx.EXPAND)

        detailsSizer.Add(
            wx.StaticText(mainPanel, label="Spectral Types:"),
            0,
            wx.ALIGN_TOP,
        )
        self.systemSpectralTypes = wx.TextCtrl(
            mainPanel,
            size=(-1, 55),
            style=wx.TE_MULTILINE,
        )
        detailsSizer.Add(self.systemSpectralTypes, 1, wx.EXPAND)

        systemEditorSizer.Add(
            detailsSizer,
            0,
            wx.ALL | wx.EXPAND,
            5,
        )

        spectralTypeHint = wx.StaticText(
            mainPanel,
            label=(
                "Separate spectral types with commas, semicolons, or new lines. "
                "Examples: G2, M4, WD, NS"
            ),
        )
        spectralTypeHint.Wrap(310)
        systemEditorSizer.Add(
            spectralTypeHint,
            0,
            wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND,
            5,
        )

        self.applySystemBtn = wx.Button(
            mainPanel,
            label="Apply Changes",
        )
        self.applySystemBtn.Bind(
            wx.EVT_BUTTON,
            self.applySystemChanges,
        )
        self.applySystemBtn.Disable()
        systemEditorSizer.Add(
            self.applySystemBtn,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
        )

        inputSizer.Add(
            systemEditorSizer,
            1,
            wx.TOP | wx.EXPAND,
            5,
        )

        self.mainSizer.Add(inputSizer, 0, wx.ALL | wx.EXPAND, 5)

        # Map display area
        mapSizer = wx.FlexGridSizer(1, 1, wx.Size(0, 0))
        mapSizer.AddGrowableCol(0)
        mapSizer.AddGrowableRow(0)
        mapSizer.SetFlexibleDirection(wx.BOTH)

        self.mapPanel = SMGMapPanel(mainPanel)
        mapSizer.Add(self.mapPanel, 1, wx.ALL | wx.EXPAND, 5)
        self.mainSizer.Add(mapSizer, 1, wx.ALL | wx.EXPAND, 5)

        # Set defaults for the inputs
        self.setDefaults()

        # Finalize display
        self.mainSizer.SetSizeHints(self)
        mainPanel.SetSizer(self.mainSizer)
        mainPanel.Layout()

        self.Bind(wx.EVT_SIZE, self.onResize)
        self.Show()

    def generateMap(self, event):
        self.params = self.createParamDict()

        self.loadOrGenerateMapData()
        self.renderCurrentMap()
        self.saveCurrentMap()
        self.drawMap(self.params["filename"])
        self.refreshSystemEditor()

    def loadOrGenerateMapData(self):
        """Load or generate the data that forms the current map."""
        self.starList = []
        self.jumpList = []

        inputFilename = self.inDataName.GetValue().strip()

        if inputFilename:
            loadData(
                inputFilename,
                self.params,
                self.starList,
                self.jumpList,
            )
        else:
            self.starList = createSystems(self.params)
            self.jumpList = findJumps(self.starList)

        print("there are", len(self.starList), "systems on the map")

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

        # createMapSymbols assigns drawnPos, which findConnections requires.
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
        )

    def saveCurrentMap(self):
        """Write the current in-memory map state to the configured DAT file."""
        writeSystemData(self.params, self.starList)
        writeConnectionData(self.params, self.jumpList)

    def refreshSystemEditor(self, selectedIndex=0):
        """Refresh the system list from the current in-memory map state."""
        self.systemList.Freeze()

        try:
            self.systemList.Clear()

            for system in self.starList:
                self.systemList.Append(
                    f"{system.name} ({system.x}, {system.y}, {system.z})"
                )
        finally:
            self.systemList.Thaw()

        if self.starList:
            selectedIndex = max(0, min(selectedIndex, len(self.starList) - 1))
            self.systemList.SetSelection(selectedIndex)
            self.showSystemDetails(selectedIndex)
        else:
            self.clearSystemDetails()

        self.mainSizer.Layout()

    def onSystemSelected(self, event):
        """Display the system selected in the list."""
        self.showSystemDetails(event.GetSelection())

    def showSystemDetails(self, index):
        """Load one system into the detail fields."""
        if index == wx.NOT_FOUND or not 0 <= index < len(self.starList):
            self.clearSystemDetails()
            return

        system = self.starList[index]
        self.selectedSystemIndex = index

        self.systemName.SetValue(system.name)
        self.systemX.SetValue(str(system.x))
        self.systemY.SetValue(str(system.y))
        self.systemZ.SetValue(str(system.z))
        self.systemStarCount.SetValue(str(system.nStars))
        self.systemSpectralTypes.SetValue(", ".join(system.stars))
        self.applySystemBtn.Enable()

    def applySystemChanges(self, event):
        """Validate and apply edits to the selected star system."""
        index = self.selectedSystemIndex

        if index == wx.NOT_FOUND or not 0 <= index < len(self.starList):
            wx.MessageBox(
                "Select a star system before applying changes.",
                "No star system selected",
                wx.OK | wx.ICON_INFORMATION,
            )
            return

        try:
            name = self.validateSystemName(
                self.systemName.GetValue(),
                index,
            )
            x = self.parseCoordinate(
                self.systemX.GetValue(),
                "X",
                1,
                self.params["maxX"],
            )
            y = self.parseCoordinate(
                self.systemY.GetValue(),
                "Y",
                1,
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
        except ValueError as error:
            wx.MessageBox(
                str(error),
                "Invalid star system data",
                wx.OK | wx.ICON_ERROR,
            )
            return

        system = self.starList[index]
        oldName = system.name

        system.name = name
        system.x = x
        system.y = y
        system.z = z
        system.mapPos = (x, y)
        system.stars = spectralTypes
        system.nStars = len(spectralTypes)

        if oldName != name:
            self.renameSystemInJumps(oldName, name)

        self.renderCurrentMap()
        self.saveCurrentMap()
        self.drawMap(self.params["filename"])
        self.refreshSystemEditor(index)

        self.SetStatusText(
            f'Changes to "{name}" were saved to the SVG and DAT files.'
        )

    def validateSystemName(self, value, selectedIndex):
        """Return a valid, unique system name."""
        name = value.strip()

        if not name:
            raise ValueError("The system name must not be empty.")

        if '"' in name:
            raise ValueError(
                'The system name must not contain a double quote (").'
            )

        for index, system in enumerate(self.starList):
            if index != selectedIndex and system.name == name:
                raise ValueError(
                    f'A star system named "{name}" already exists.'
                )

        return name

    def parseCoordinate(self, value, label, minimum, maximum):
        """Parse and validate one map coordinate."""
        try:
            coordinate = int(value.strip())
        except ValueError as error:
            raise ValueError(
                f"{label} must be a whole number."
            ) from error

        if not minimum <= coordinate <= maximum:
            raise ValueError(
                f"{label} must be between {minimum} and {maximum}."
            )

        return coordinate

    def parseSpectralTypes(self, value):
        """Parse and validate the comma-separated spectral type list."""
        spectralTypes = [
            re.sub(r"\s+", "", item).upper()
            for item in re.split(r"[,;\r\n]+", value)
            if item.strip()
        ]

        if not spectralTypes:
            raise ValueError(
                "A star system must contain at least one star."
            )

        if len(spectralTypes) > 10:
            raise ValueError(
                "The map renderer supports at most 10 stars per system."
            )

        pattern = re.compile(
            r"^(?:BD|WD|NS|BH|[OBAFGKM][0-9]|[FGKM][0-9](?:III|I))$"
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
                f"{invalidText}. Use values such as G2, M4, K0III, "
                "BD, WD, NS, or BH. Main-sequence stars are written "
                "without a trailing V."
            )

        return spectralTypes

    def renameSystemInJumps(self, oldName, newName):
        """Keep existing jump connections valid after a system rename."""
        self.jumpList = [
            (
                newName if startName == oldName else startName,
                newName if endName == oldName else endName,
            )
            for startName, endName in self.jumpList
        ]

    def clearSystemDetails(self):
        """Clear the system detail fields when no map is loaded."""
        self.selectedSystemIndex = wx.NOT_FOUND
        self.systemName.SetValue("")
        self.systemX.SetValue("")
        self.systemY.SetValue("")
        self.systemZ.SetValue("")
        self.systemStarCount.SetValue("")
        self.systemSpectralTypes.SetValue("")
        self.applySystemBtn.Disable()

    def resetParameters(self, event):
        self.setDefaults()

    def setDefaults(self):
        self.xSize.SetValue(20)
        self.ySize.SetValue(20)
        self.zSize.SetValue(20)
        self.stellarDensity.SetValue(0.004)
        self.textScale.SetValue(1)
        self.outMapName.SetValue("sampleMap.svg")
        self.outDataName.SetValue("sampleMap.dat")
        self.inDataName.SetValue("")
        self.printZ.SetValue(True)

    def createParamDict(self):
        params = {}
        params["maxX"] = self.xSize.GetValue()
        params["maxY"] = self.ySize.GetValue()

        zValue = self.zSize.GetValue() // 2
        params["minZ"] = -zValue
        params["maxZ"] = zValue

        if self.zSize.GetValue() % 2 == 0:
            params["minZ"] += 1

        params["stellarDensity"] = self.stellarDensity.GetValue()
        params["filename"] = self.outMapName.GetValue()
        params["datafile"] = self.outDataName.GetValue()
        params["scale"] = self.textScale.GetValue()
        params["printZ"] = self.printZ.GetValue()

        return params

    def drawMap(self, file):
        self.mapPanel.setMap(file)
        self.mainSizer.Layout()
        self.Update()
        self.Refresh()

    def onResize(self, event):
        self.Update()
        self.Refresh()
        wx.Event.Skip(event)