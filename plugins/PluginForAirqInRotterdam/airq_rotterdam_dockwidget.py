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

        #self.checkbox_Hospitals.clicked.connect(self.showHospitals)
        #self.comboHospital.addItem(blah)
    def showHospitals(self):
        pass

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

#######
#   Data functions
#######
    def openScenario(self,filename=""):
        scenario_file = (self.plugin_dir,'sample_data2','GEO1005_SDSS.qgs')
        self.iface.addProject(unicode(scenario_file))

