import wx
import wx.lib.intctrl
from wx.lib.masked import NumCtrl


class MapParametersPanel(wx.Panel):
    """Controls for map files, display and random generation."""

    def __init__(
            self,
            parent,
            controller,
    ):
        super().__init__(parent)

        self.controller = controller

        self.createControls()
        self.setDefaults()

    def SetStatusText(
            self,
            text,
    ):
        self.controller.SetStatusText(
            text
        )

    def refreshInputPanelLayout(self):
        self.controller.refreshInputPanelLayout()

    def onLoadMap(
            self,
            event,
    ):
        self.controller.loadMap(
            event
        )

    def onGenerateMap(
            self,
            event,
    ):
        self.controller.generateMap(
            event
        )

    def onExportPng(
            self,
            event,
    ):
        self.controller.onExportPng(
            event
        )

    def createControls(self):
        """Create map parameter controls."""

        panel_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        self.createFilesAndDisplayControls(
            panel_sizer
        )

        self.createRandomGenerationControls(
            panel_sizer
        )

        self.SetSizer(
            panel_sizer
        )

    def createFilesAndDisplayControls(
            self,
            target_sizer,
    ):
        """Create file and display controls."""

        self.textScale = NumCtrl(
            self,
            min=0.25,
            fractionWidth=2,
        )

        self.addControlRow(
            target_sizer,
            "Text Scale:",
            self.textScale,
        )

        self.outMapName = wx.TextCtrl(
            self
        )

        self.addControlRow(
            target_sizer,
            "Output Map Filename:",
            self.outMapName,
        )

        self.dataName = wx.TextCtrl(
            self
        )

        self.addControlRow(
            target_sizer,
            "Data Filename:",
            self.dataName,
        )

        print_z_row = wx.BoxSizer(
            wx.HORIZONTAL
        )

        print_z_row.Add(
            wx.StaticText(
                self,
                label="Print Z coordinate:",
            ),
            1,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.printZ = wx.CheckBox(
            self
        )

        print_z_row.Add(
            self.printZ,
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        target_sizer.Add(
            print_z_row,
            0,
            wx.ALL | wx.EXPAND,
            5,
            )

        button_sizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        load_button = wx.Button(
            self,
            label="Load Map",
        )

        load_button.Bind(
            wx.EVT_BUTTON,
            self.onLoadMap,
        )

        button_sizer.Add(
            load_button,
            0,
            wx.RIGHT,
            5,
        )

        self.exportPngButton = wx.Button(
            self,
            label="Export PNG",
        )

        self.exportPngButton.Bind(
            wx.EVT_BUTTON,
            self.onExportPng,
        )

        self.exportPngButton.Disable()

        button_sizer.Add(
            self.exportPngButton,
            0,
            wx.RIGHT,
            5,
        )

        reset_button = wx.Button(
            self,
            label="Reset Values",
        )

        reset_button.Bind(
            wx.EVT_BUTTON,
            self.resetParameters,
        )

        button_sizer.Add(
            reset_button,
            0,
        )

        target_sizer.Add(
            button_sizer,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
            )

    def createRandomGenerationControls(
            self,
            target_sizer,
    ):
        """Create random map generation controls."""

        self.xSize = wx.lib.intctrl.IntCtrl(
            self,
            min=1,
        )

        self.addControlRow(
            target_sizer,
            "Map Width (x):",
            self.xSize,
        )

        self.ySize = wx.lib.intctrl.IntCtrl(
            self,
            min=1,
        )

        self.addControlRow(
            target_sizer,
            "Map Height (y):",
            self.ySize,
        )

        self.zSize = wx.lib.intctrl.IntCtrl(
            self,
            min=1,
        )

        self.addControlRow(
            target_sizer,
            "Map Thickness (z):",
            self.zSize,
        )

        self.stellarDensity = NumCtrl(
            self,
            min=0,
            fractionWidth=4,
        )

        self.addControlRow(
            target_sizer,
            "Stellar Density:",
            self.stellarDensity,
        )

        generate_button = wx.Button(
            self,
            label="Generate Random Map",
        )

        generate_button.Bind(
            wx.EVT_BUTTON,
            self.onGenerateMap,
        )

        target_sizer.Add(
            generate_button,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
            )

    def addControlRow(
            self,
            section_sizer,
            label,
            control,
    ):
        row = wx.BoxSizer(
            wx.HORIZONTAL
        )

        row.Add(
            wx.StaticText(
                self,
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
    
        section_sizer.Add(
            row,
            0,
            wx.ALL | wx.EXPAND,
            5,
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

        z_value = self.zSize.GetValue() // 2

        params["minZ"] = -z_value
        params["maxZ"] = z_value

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

    def refreshExportControls(self):
        """Enable export controls when a map exists."""

        self.exportPngButton.Enable(
            bool(self.controller.params)
        )

    def setExportEnabled(
        self,
        enabled,
    ):
        self.exportPngButton.Enable(
            enabled
        )

