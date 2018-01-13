# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginForAirqInRotterdamDockWidget
                                 A QGIS plugin
 Plugin For see effect of Air Quality In Rotterdam
                             -------------------
        begin                : 2017-12-15
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Group05_2017
        email                : juanchodpg@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from PyQt4.QtGui import QColor, QAction
from PyQt4.QtCore import pyqtSignal
from qgis.core import QgsColorRampShader, QgsRasterShader, QgsSingleBandPseudoColorRenderer

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'airq_rotterdam_dockwidget_base.ui'))


class PluginForAirqInRotterdamDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(PluginForAirqInRotterdamDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.iface=iface
        self.plugin_dir = os.path.dirname(__file__)
        self.openScenario()
        self.initCheckBoxes()
        self.initComboBox()
        self.initslider()
        self.initSelectButton()
        self.initZoomButtons()

    def initZoomButtons(self):
        self.zoomSelectionButton.clicked.connect(self.iface.actionZoomToSelected().trigger)
        self.fullZoomButton.clicked.connect(self.iface.actionZoomFullExtent().trigger)

    def initSelectButton(self):
        self.selectButton.toggled.connect(self.changeTool)
        self.getLayer("Rotterdam_neighbourhoods_cleaned").selectionChanged.connect(self.updateInfo)

    def changeTool(self, checked):
        if checked:
            self.iface.setActiveLayer(self.getLayer("Rotterdam_neighbourhoods_cleaned"))
            self.iface.actionSelect().trigger()
        else:
            self.iface.actionPan().trigger()

    def updateInfo(self):
        layer = self.getLayer("Rotterdam_neighbourhoods_cleaned")
        selected_features = layer.selectedFeatures()
        info = "<pre>"
        for i in selected_features:
            info += "<B>{}</B>\n".format(i.attribute("BU_NAAM"))
            info += "Area: {}ha\n".format(i.attribute("OPP_TOT"))
            info += "Population count: {}\n".format(i.attribute("AANT_INW"))
            info += "  0-14y: {}%\n".format(i.attribute("P_00_14_JR"))
            info += "  15-24y: {}%\n".format(i.attribute("P_15_24_JR"))
            info += "  25-44y: {}%\n".format(i.attribute("P_25_44_JR"))
            info += "  45-64y: {}%\n".format(i.attribute("P_45_64_JR"))
            info += "  65+y: {}%\n".format(i.attribute("P_65_EO_JR"))
            info += "Population density: {}pop/km2\n".format(i.attribute("BEV_DICHTH"))
            info += "No. of households: {}\n".format(i.attribute("AANTAL_HH"))
            info += "  single person hh: {}%\n".format(i.attribute("P_EENP_HH"))
            info += "  mult. person hh w/o children: {}%\n".format(i.attribute("P_HH_Z_K"))
            info += "  mult. person hh with children: {}%\n".format(i.attribute("P_HH_M_K"))
            info += "No. of businesses: {}\n".format(i.attribute("A_BEDV"))
            info += "No. of industrial businesses: {}\n".format(i.attribute("A_BED_BF"))
            info += "\n"
        info += "</pre>"
        info = info.replace("-99999999%", "-")
        info = info.replace("-99999999ha", "-")
        info = info.replace("-99999999pop/km2", "-")
        info = info.replace("-99999999", "-")
        self.neighbourhoodInfo.setHtml(info)

    def initslider(self):
        self.updateMinMidMax()
        self.comboBoxType.currentIndexChanged.connect(self.updateMinMidMax)
        self.updateCurrentValue()
        self.sliderMaxLevel.valueChanged.connect(self.updateCurrentValue)
        self.comboBoxType.currentIndexChanged.connect(self.updateCurrentValue)
        self.updateMap()

    def updateMap(self):
        fcn = QgsColorRampShader()
        fcn.setColorRampType(QgsColorRampShader.INTERPOLATED)
        maxValue = self.sliderMaxLevel.sliderPosition()
        lst = [QgsColorRampShader.ColorRampItem(0, QColor(128, 192, 255)),
               QgsColorRampShader.ColorRampItem(maxValue * 0.5, QColor(0, 255, 0)),
               QgsColorRampShader.ColorRampItem(maxValue * 0.75, QColor(255, 255, 0)),
               QgsColorRampShader.ColorRampItem(maxValue - 0.0001, QColor(255, 128, 0)),
               QgsColorRampShader.ColorRampItem(maxValue, QColor(255, 0, 0))]
        fcn.setColorRampItemList(lst)
        shader = QgsRasterShader()
        shader.setRasterShaderFunction(fcn)
        layer = self.getCurrentLayer()
        renderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), 1, shader)
        layer.setRenderer(renderer)
        if hasattr(layer, "setCacheImage"):
            layer.setCacheImage(None)
        layer.triggerRepaint()

    def getCurrentLayer(self):
        if self.comboBoxType.currentText() == "PM 2.5":
            return self.getLayer("pm25_concentration")
        elif self.comboBoxType.currentText() == "PM 10":
            return self.getLayer("pm10_concentration")
        elif self.comboBoxType.currentText() == "NO2":
            return self.getLayer("no2_concentration")
        else:
            raise KeyError("unexpected pollution type")

    def updateCurrentValue(self):
        self.labelCurrentValue.setText("Value: " + str(self.sliderMaxLevel.sliderPosition()) + " ug/m3")
        self.updateMap()

    def updateMinMidMax(self):
        if self.comboBoxType.currentText() == "PM 2.5":
            self.sliderMaxLevel.setRange(12, 25)
            self.sliderMaxLevel.setTickInterval(1)
        elif self.comboBoxType.currentText() == "PM 10":
            self.sliderMaxLevel.setRange(20, 40)
            self.sliderMaxLevel.setTickInterval(1)
        elif self.comboBoxType.currentText() == "NO2":
            self.sliderMaxLevel.setRange(30, 40)
            self.sliderMaxLevel.setTickInterval(1)
        else:
            raise KeyError("unexpected pollution type:" )

        minimum = self.sliderMaxLevel.minimum()
        maximum = self.sliderMaxLevel.maximum()
        self.labelMin.setText(str(minimum))
        self.labelMid.setText(str((minimum + maximum) / 2))
        self.labelMax.setText(str(maximum))

    def initComboBox(self):
        typeList = ["PM 2.5", "PM 10", "NO2"]
        self.comboBoxType.insertItems(0, typeList)
        self.updateComboBox()
        self.comboBoxType.currentIndexChanged.connect(self.updateComboBox)

    def updateComboBox(self):
        layer = self.getLayer("pm25_concentration")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, self.comboBoxType.currentText() == "PM 2.5")

        layer = self.getLayer("pm10_concentration")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, self.comboBoxType.currentText() == "PM 10")

        layer = self.getLayer("no2_concentration")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, self.comboBoxType.currentText() == "NO2")


    def initCheckBoxes(self):
        legend = self.iface.legendInterface()
        self.checkBoxHospitals.setChecked(legend.isLayerVisible(self.getLayer("Hospitals")))
        self.checkBoxSchools.setChecked(legend.isLayerVisible(self.getLayer("Schools")))
        self.checkBoxNursingHomes.setChecked(legend.isLayerVisible(self.getLayer("Nursing_homes")))

        self.checkBoxHospitals.clicked.connect(self.showHospitals)
        self.checkBoxSchools.clicked.connect(self.showSchools)
        self.checkBoxNursingHomes.clicked.connect(self.showNursingHomes)

    def showHospitals(self, checked):
        layer = self.getLayer("Hospitals")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)

    def showSchools(self, checked):
        layer = self.getLayer("Schools")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)

    def showNursingHomes(self, checked):
        layer = self.getLayer("Nursing_homes")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)

    def getLayer(self, name):
        legend = self.iface.legendInterface()
        for layer in legend.layers():
            if layer.name() == name:
                return layer
        raise KeyError("layer does not exist")

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

#######
#   Data functions
#######
    def openScenario(self):
        scenario_file =  os.path.join(self.plugin_dir,'sample_data2','GEO1005_SDSS.qgs')
        self.iface.addProject(unicode(scenario_file))

