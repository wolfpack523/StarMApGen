import wx

from Planet import Planet


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

        main_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        form_sizer = wx.FlexGridSizer(
            cols=2,
            vgap=8,
            hgap=8,
        )

        form_sizer.AddGrowableCol(
            1,
            1,
        )

        form_sizer.Add(
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

        form_sizer.Add(
            self.nameControl,
            1,
            wx.EXPAND,
        )

        form_sizer.Add(
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

        form_sizer.Add(
            self.typeChoice,
            1,
            wx.EXPAND,
        )

        form_sizer.Add(
            wx.StaticText(
                self,
                label="Classification:",
            ),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )

        self.classificationChoice = (
            wx.Choice(
                self,
                choices=list(
                    Planet.CLASSIFICATIONS
                ),
            )
        )

        form_sizer.Add(
            self.classificationChoice,
            1,
            wx.EXPAND,
        )

        main_sizer.Add(
            form_sizer,
            1,
            wx.ALL | wx.EXPAND,
            12,
            )

        button_sizer = (
            self.CreateButtonSizer(
                wx.OK | wx.CANCEL
            )
        )

        main_sizer.Add(
            button_sizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            12,
            )

        self.SetSizerAndFit(
            main_sizer
        )

        if planet is not None:
            self.loadPlanet(
                planet
            )
        else:
            self.typeChoice.SetSelection(
                0
            )

            self.classificationChoice.SetStringSelection(
                Planet.DEFAULT_CLASSIFICATION
            )

        self.nameControl.SetFocus()

    def loadPlanet(
            self,
            planet,
    ):
        """Load an existing planet into the dialog."""

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
            return (
                Planet.DEFAULT_CLASSIFICATION
            )

        return Planet.CLASSIFICATIONS[
            selection
        ]