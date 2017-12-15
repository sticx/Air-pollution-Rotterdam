# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PluginForAirqInRotterdam
                                 A QGIS plugin
 Plugin For see effect of Air Quality In Rotterdam
                             -------------------
        begin                : 2017-12-15
        copyright            : (C) 2017 by Group05_2017
        email                : juanchodpg@hotmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PluginForAirqInRotterdam class from file PluginForAirqInRotterdam.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .airq_rotterdam import PluginForAirqInRotterdam
    return PluginForAirqInRotterdam(iface)
