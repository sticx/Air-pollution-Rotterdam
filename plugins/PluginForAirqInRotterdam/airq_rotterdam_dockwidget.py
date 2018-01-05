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
from PyQt4.QtCore import pyqtSignal

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

    def initslider(self):
        self.updateMinMidMax()
        self.comboBoxType.currentIndexChanged.connect(self.updateMinMidMax)
        self.updateCurrentValue()
        self.sliderMaxLevel.sliderMoved.connect(self.updateCurrentValue)
        self.comboBoxType.currentIndexChanged.connect(self.updateCurrentValue)

    def updateCurrentValue(self):
        self.labelCurrentValue.setText("Value: " + str(self.sliderMaxLevel.sliderPosition()) + " ug/m3")

    def updateMinMidMax(self):
        if self.comboBoxType.currentText() == "PM 2.5":
            self.sliderMaxLevel.setRange(0, 20)
            self.sliderMaxLevel.setTickInterval(5)
        elif self.comboBoxType.currentText() == "PM 10":
            self.sliderMaxLevel.setRange(0, 40)
        elif self.comboBoxType.currentText() == "NO2":
            self.sliderMaxLevel.setRange(0, 50)

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

