import wx
import wx.lib.intctrl


class MapBoundsPanel(wx.Panel):
    """Controls for displaying and extending map bounds."""

    def __init__(
            self,
            parent,
            controller,
    ):
        super().__init__(parent)

        self.controller = controller

        self.createControls()

    @property
    def params(self):
        return self.controller.params

    def SetStatusText(
            self,
            text,
    ):
        self.controller.SetStatusText(
            text
        )

    def saveAndRedrawCurrentMap(self):
        self.controller.saveAndRedrawCurrentMap()

    def refreshInputPanelLayout(self):
        self.controller.refreshInputPanelLayout()

    def hasCurrentMapBounds(self):
        return (
            self.controller
            .hasCurrentMapBounds()
        )

    def createControls(self):
        """Create controls for extending the map."""

        panel_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        self.mapBoundsLabel = wx.StaticText(
            self,
            label="No map loaded.",
        )

        self.mapBoundsLabel.Wrap(
            330
        )

        panel_sizer.Add(
            self.mapBoundsLabel,
            0,
            wx.ALL | wx.EXPAND,
            5,
            )

        amount_sizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        amount_sizer.Add(
            wx.StaticText(
                self,
                label="Extend by:",
            ),
            1,
            wx.ALIGN_CENTER_VERTICAL
            | wx.RIGHT,
            5,
            )

        self.extendAmount = (
            wx.lib.intctrl.IntCtrl(
                self,
                min=1,
            )
        )

        self.extendAmount.SetValue(
            5
        )

        self.extendAmount.Disable()

        amount_sizer.Add(
            self.extendAmount,
            0,
        )

        panel_sizer.Add(
            amount_sizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
            )

        button_grid = wx.GridSizer(
            rows=2,
            cols=3,
            vgap=5,
            hgap=5,
        )

        button_definitions = [
            ("X -", "x-"),
            ("Y -", "y-"),
            ("Z -", "z-"),
            ("X +", "x+"),
            ("Y +", "y+"),
            ("Z +", "z+"),
        ]

        self.mapBoundsButtons = []

        for label, direction in button_definitions:
            button = wx.Button(
                self,
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

            button_grid.Add(
                button,
                1,
                wx.EXPAND,
            )

        panel_sizer.Add(
            button_grid,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
            )

        self.SetSizer(
            panel_sizer
        )

    def refreshMapBoundsControls(self):
        """Display the current absolute map bounds."""

        required_keys = (
            "minX",
            "maxX",
            "minY",
            "maxY",
            "minZ",
            "maxZ",
        )

        has_map_bounds = (
                bool(self.params)
                and all(
            key in self.params
            for key in required_keys
        )
        )

        if not has_map_bounds:
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

        direction_definitions = {
            "x-": ("minX", -1, "negative X"),
            "x+": ("maxX", 1, "positive X"),
            "y-": ("minY", -1, "negative Y"),
            "y+": ("maxY", 1, "positive Y"),
            "z-": ("minZ", -1, "negative Z"),
            "z+": ("maxZ", 1, "positive Z"),
        }

        if direction not in direction_definitions:
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

        parameter_name, factor, label = (
            direction_definitions[direction]
        )

        # This updates the actual map model.
        self.params[parameter_name] += (
                factor * amount
        )

        self.saveAndRedrawCurrentMap()

        self.SetStatusText(
            f"Map extended by {amount} "
            f"unit(s) towards {label}."
        )