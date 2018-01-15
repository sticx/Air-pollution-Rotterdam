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

import os.path
from PyQt4 import QtGui, uic
from PyQt4.QtGui import QColor, QAction, QFileDialog
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
        self.initExportButton()
        self.initRadioButtons()

    def initExportButton(self):
        self.buttonExport.clicked.connect(self.export)

    def export(self):
        fileName = QFileDialog.getSaveFileName(self, "Export to file", ".", "*.txt")
        if fileName == None:
            return

        with open(fileName, "w") as fh:
            fh.write("========================================\n"
                     "        AIR QUALITY IN ROTTERDAM\n"
                     "========================================\n"
                     "\n")

            fh.write("Pollution type: " + self.comboBoxType.currentText() + "\n"
                     "Maximal level: " + str(self.sliderMaxLevel.sliderPosition()) + " ug/m3\n"
                     "\n\n")

            if self.textNotesHospitals.toPlainText() != "":
                fh.write("               USER NOTES\n"
                         "========================================\n"
                         "HOSPITALS\n" +
                         self.textNotesHospitals.toPlainText() + "\n"
                         "\n")

            if self.textNotesSchools.toPlainText() != "":
                fh.write("SCHOOLS\n" +
                         self.textNotesSchools.toPlainText() + "\n"
                         "\n")

            if self.textNotesNursingHomes.toPlainText() != "":
                fh.write("NURSING HOMES\n" +
                         self.textNotesNursingHomes.toPlainText() + "\n"
                         "\n\n")

            if self.generateInfo(False) != "":
                fh.write("       NEIGHBOURHOOD INFORMATION\n"
                         "========================================\n" +
                         self.generateInfo(False) + "\n"
                         "\n\n")


    def initZoomButtons(self):
        self.zoomSelectionButton.clicked.connect(self.iface.actionZoomToSelected().trigger)
        self.fullZoomButton.clicked.connect(self.iface.actionZoomFullExtent().trigger)

    def initSelectButton(self):
        self.changeTool(False)
        self.selectButton.toggled.connect(self.changeTool)
        self.getLayer("Rotterdam_neighbourhoods_cleaned").selectionChanged.connect(self.updateInfo)

    def changeTool(self, checked):
        if checked:
            self.iface.setActiveLayer(self.getLayer("Rotterdam_neighbourhoods_cleaned"))
            self.iface.actionSelect().trigger()
        else:
            self.iface.actionPan().trigger()

    def updateInfo(self):
        info = self.generateInfo(True)
        self.neighbourhoodInfo.setHtml(info)

    def generateInfo(self, is_html):
        layer = self.getLayer("Rotterdam_neighbourhoods_cleaned")
        selected_features = layer.selectedFeatures()
        info = ""
        if is_html:
            info += "<pre>"

        for i in selected_features:
            if is_html:
                info += "<B>{}</B>\n".format(i.attribute("BU_NAAM"))
            else:
                info += "{}\n".format(i.attribute("BU_NAAM").upper())

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

        if is_html:
            info += "</pre>"

        info = info.replace("-99999999%", "-")
        info = info.replace("-99999999ha", "-")
        info = info.replace("-99999999pop/km2", "-")
        info = info.replace("-99999999", "-")

        return info

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

    def initRadioButtons(self):
        legend = self.iface.legendInterface()
        # Set Default
        self.radioButtonSatBgOff.setChecked(True)
        # Create a Group and make it exclusive
        self.radioGrp.setExclusive(True)
        # Add radio buttons to group
        self.radioGrp.addButton(self.radioButtonSatBgOn) #online map
        self.radioGrp.addButton(self.radioButtonSatBgOff) #offline map
        self.radioGrp.addButton(self.radioButtonGmapsBgOn) #online map
        self.radioGrp.addButton(self.radioButtonGmapsBgOff) #offline map
        #actions
        self.radioButtonSatBgOn.setChecked(legend.isLayerVisible(self.getLayer("Google Satellite")))
        self.radioButtonSatBgOff.setChecked(legend.isLayerVisible(self.getLayer("SatelliteBackground")))
        self.radioButtonGmapsBgOn.setChecked(legend.isLayerVisible(self.getLayer("Google Streets")))
        self.radioButtonGmapsBgOff.setChecked(legend.isLayerVisible(self.getLayer("GmapBackground")))
        #connect buttons
        self.radioButtonSatBgOn.toggled.connect(self.showSatBgOnline)
        self.radioButtonSatBgOff.toggled.connect(self.showSatBgOff)
        self.radioButtonGmapsBgOn.toggled.connect(self.showGmapsBgOnline)
        self.radioButtonGmapsBgOff.toggled.connect(self.showGmapsBgOff)
        #https: // stackoverflow.com / questions / 1753939 / qt - python - radiobutton - activate - event
    def showSatBgOnline(self, checked):
        layer = self.getLayer("Google Satellite")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)
    def showSatBgOff(self, checked):
        layer = self.getLayer("SatelliteBackground")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)
    def showGmapsBgOnline(self, checked):
        layer = self.getLayer("Google Streets")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)
    def showGmapsBgOff(self, checked):
        layer = self.getLayer("GmapBackground")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)

    def initCheckBoxes(self):
        legend = self.iface.legendInterface()
        self.checkBoxHospitals.setChecked(legend.isLayerVisible(self.getLayer("Hospitals")))
        self.checkBoxSchools.setChecked(legend.isLayerVisible(self.getLayer("Schools")))
        self.checkBoxNursingHomes.setChecked(legend.isLayerVisible(self.getLayer("Nursing_homes")))
        self.checkBoxIndustry.setChecked(legend.isLayerVisible(self.getLayer("Industry")))
        self.checkBoxRoads.setChecked(legend.isLayerVisible(self.getLayer("Roads")))

        self.checkBoxHospitals.clicked.connect(self.showHospitals)
        self.checkBoxSchools.clicked.connect(self.showSchools)
        self.checkBoxNursingHomes.clicked.connect(self.showNursingHomes)
        self.checkBoxIndustry.clicked.connect(self.showIndustry)
        self.checkBoxRoads.clicked.connect(self.showRoads)

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

    def showIndustry(self, checked):
        layer = self.getLayer("Industry")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)

    def showRoads(self, checked):
        layer = self.getLayer("Roads")
        legend = self.iface.legendInterface()
        legend.setLayerVisible(layer, checked)

    def getLayer(self, name):
        legend = self.iface.legendInterface()
        for layer in legend.layers():
            if layer.name() == name:
                return layer
        # raise KeyError("layer does not exist")

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

#######
#   Data functions
#######
    def openScenario(self):
        scenario_file =  os.path.join(self.plugin_dir,'sample_data2','GEO1005_SDSS.qgs')
        self.iface.addProject(unicode(scenario_file))

