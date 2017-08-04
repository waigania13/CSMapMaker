# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CSMapMaker
                                 A QGIS plugin
 csmap plugin
                             -------------------
        begin                : 2017-01-31
        copyright            : (C) 2017 by Kosuke ASAHI
        email                : waigania13@gmail.com
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
    """Load CSMap class from file CSMap.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .csmap import CSMap
    return CSMap(iface)
