import wx

from domain.Planet import Planet
from ui.dialogs.PlanetDialog import PlanetDialog


class PlanetEditorPanel(wx.Panel):
    """Editor for the planets of one star system."""

    def __init__(
            self,
            parent,
            on_changed,
            set_status_text,
    ):
        super().__init__(parent)

        self.onChanged = on_changed
        self.setStatusText = set_status_text

        self.editedPlanets = []

        self.createControls()

    def createControls(self):
        panel_sizer = wx.BoxSizer(
            wx.VERTICAL
        )

        panel_sizer.Add(
            wx.StaticText(
                self,
                label="Planets:",
            ),
            0,
            wx.LEFT | wx.RIGHT | wx.TOP,
            5,
            )

        self.planetListControl = wx.ListCtrl(
            self,
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

        panel_sizer.Add(
            self.planetListControl,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.EXPAND,
            5,
            )

        button_sizer = wx.BoxSizer(
            wx.HORIZONTAL
        )

        self.addPlanetButton = wx.Button(
            self,
            label="Add Planet",
        )

        self.addPlanetButton.Bind(
            wx.EVT_BUTTON,
            self.addPlanet,
        )

        button_sizer.Add(
            self.addPlanetButton,
            0,
            wx.RIGHT,
            5,
        )

        self.editPlanetButton = wx.Button(
            self,
            label="Edit Planet",
        )

        self.editPlanetButton.Bind(
            wx.EVT_BUTTON,
            self.editPlanet,
        )

        self.editPlanetButton.Disable()

        button_sizer.Add(
            self.editPlanetButton,
            0,
            wx.RIGHT,
            5,
        )

        self.removePlanetButton = wx.Button(
            self,
            label="Remove Planet",
        )

        self.removePlanetButton.Bind(
            wx.EVT_BUTTON,
            self.removePlanet,
        )

        self.removePlanetButton.Disable()

        button_sizer.Add(
            self.removePlanetButton,
            0,
        )

        panel_sizer.Add(
            button_sizer,
            0,
            wx.LEFT
            | wx.RIGHT
            | wx.BOTTOM
            | wx.ALIGN_RIGHT,
            5,
            )

        self.SetSizer(
            panel_sizer
        )

    def setPlanets(
            self,
            planets,
    ):
        """Replace the temporary planet editor state."""

        self.editedPlanets = [
            Planet(
                name=planet.name,
                planetType=planet.planetType,
                classification=planet.classification,
            )
            for planet in planets
        ]

        self.refreshPlanetEditor()

    def getPlanets(self):
        """Return copies of the currently edited planets."""

        return [
            Planet(
                name=planet.name,
                planetType=planet.planetType,
                classification=planet.classification,
            )
            for planet in self.editedPlanets
        ]

    def clear(self):
        self.editedPlanets = []

        self.planetListControl.DeleteAllItems()

        self.addPlanetButton.Disable()
        self.editPlanetButton.Disable()
        self.removePlanetButton.Disable()

    def setEnabled(
            self,
            enabled,
    ):
        self.addPlanetButton.Enable(
            enabled
        )

        if not enabled:
            self.editPlanetButton.Disable()
            self.removePlanetButton.Disable()
        else:
            self.updatePlanetButtons()

    def refreshPlanetEditor(self):
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
        self.updatePlanetButtons()
        event.Skip()

    def updatePlanetButtons(self):
        selected_index = (
            self.planetListControl
            .GetFirstSelected()
        )

        has_selection = (
                selected_index != -1
        )

        self.editPlanetButton.Enable(
            has_selection
        )

        self.removePlanetButton.Enable(
            has_selection
        )

    def validatePlanetName(
            self,
            name,
            ignored_index=-1,
    ):
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
                    index != ignored_index
                    and planet.name.casefold()
                    == name.casefold()
            ):
                raise ValueError(
                    f'A planet named "{name}" already exists '
                    "in this system."
                )

        return name

    def addPlanet(self, event):
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

            self.changed()

            self.refreshPlanetEditor()

        finally:
            dialog.Destroy()

    def editPlanet(self, event):
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
                    ignored_index=index,
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

            self.changed()

            self.refreshPlanetEditor()

            self.planetListControl.Select(
                index
            )

        finally:
            dialog.Destroy()

    def removePlanet(self, event):
        index = (
            self.planetListControl
            .GetFirstSelected()
        )

        if index == -1:
            return

        del self.editedPlanets[index]

        self.changed()

        self.refreshPlanetEditor()

    def changed(self):
        self.onChanged()

        self.setStatusText(
            "Planet list changed. "
            "Use Apply Changes to save."
        )