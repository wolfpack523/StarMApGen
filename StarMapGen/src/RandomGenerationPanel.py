import wx
import wx.lib.intctrl
from wx.lib.masked import NumCtrl


class RandomGenerationPanel(wx.Panel):
    """Controls for random map generation."""

    def __init__(
            self,
            parent,
            controller,
    ):
        super().__init__(parent)

        self.controller = controller

        self.createControls()
        self.setDefaults()

    def createControls(self):
        panelSizer = wx.BoxSizer(
            wx.VERTICAL
        )

        self.xSize = wx.lib.intctrl.IntCtrl(
            self,
            min=1,
        )

        self.addControlRow(
            panelSizer,
            "Map Width (x):",
            self.xSize,
        )

        self.ySize = wx.lib.intctrl.IntCtrl(
            self,
            min=1,
        )

        self.addControlRow(
            panelSizer,
            "Map Height (y):",
            self.ySize,
        )

        self.zSize = wx.lib.intctrl.IntCtrl(
            self,
            min=1,
        )

        self.addControlRow(
            panelSizer,
            "Map Thickness (z):",
            self.zSize,
        )

        self.stellarDensity = NumCtrl(
            self,
            min=0,
            fractionWidth=4,
        )

        self.addControlRow(
            panelSizer,
            "Stellar Density:",
            self.stellarDensity,
        )

        generateButton = wx.Button(
            self,
            label="Generate Random Map",
        )

        generateButton.Bind(
            wx.EVT_BUTTON,
            self.onGenerateMap,
        )

        panelSizer.Add(
            generateButton,
            0,
            wx.ALL | wx.ALIGN_RIGHT,
            5,
            )

        self.SetSizer(
            panelSizer
        )

    def addControlRow(
            self,
            targetSizer,
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

        targetSizer.Add(
            row,
            0,
            wx.ALL | wx.EXPAND,
            5,
            )

    def onGenerateMap(
            self,
            event,
    ):
        self.controller.generateMap(
            event
        )

    def setDefaults(self):
        self.xSize.SetValue(20)
        self.ySize.SetValue(20)
        self.zSize.SetValue(20)

        self.stellarDensity.SetValue(
            0.004
        )