# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CSMapMaker
                                 A QGIS plugin
 CSMapMaker plugin
                              -------------------
        begin                : 2017-01-31
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Kosuke ASAHI
        email                : waigania13@gmail.com
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
from __future__ import absolute_import
from builtins import object
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon, QPalette, QColor
# Initialize Qt resources from file resources.py
from qgis.core import QgsApplication 
from . import resources
# Import the code for the dialog
from .csmap_dialog import CSMapDialog
import os
from .csmap_make import CSMapMake
import processing


class CSMap(object):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'CSMap_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = CSMapDialog()
        self.dlg.button_box.accepted.connect(self.csmap)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CSMapMaker')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CSMap')
        self.toolbar.setObjectName(u'CSMap')
 
        # set default mode
        self.csmap_single_process = "SINGLE"
        self.csmap_batch_process = "BATCHPROCESS"
        self.csmap_process = self.csmap_single_process

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('CSMap', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToRasterMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/CSMap/images/csmap.png'
        self.add_action(
            icon_path,
            text=self.tr(u'CSMapMaker'),
            callback=self.run,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/CSMap/images/csmap-batch.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Batch Processing'),
            callback=self.run_batch,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginRasterMenu(
                self.tr(u'&CSMapMaker'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        self.csmap_process = self.csmap_single_process

        # hide not need item
        self.dlg.input_folder_label.hide()
        self.dlg.input_folder_edit.hide()
        self.dlg.input_folder_select.hide()
        self.dlg.output_folder_label.hide()
        self.dlg.output_folder_edit.hide()
        self.dlg.output_folder_select.hide()
        self.dlg.load_flg.hide()

        # show need item
        self.dlg.demlayer_label.show()
        self.dlg.demlayer_box.show()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def run_batch(self):
        """Run method that performs all the real work"""
        self.csmap_process = self.csmap_batch_process

        # show need item
        self.dlg.input_folder_label.show()
        self.dlg.input_folder_edit.show()
        self.dlg.input_folder_edit.setText("")
        self.dlg.input_folder_select.show()
        self.dlg.output_folder_label.show()
        self.dlg.output_folder_edit.show()
        self.dlg.output_folder_edit.setText("")
        self.dlg.output_folder_select.show()
        self.dlg.load_flg.show()

        # hide not need item
        self.dlg.demlayer_label.hide()
        self.dlg.demlayer_box.hide()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass

    def csmap(self): 
        mode = self.dlg.csmap_mode.checkedId()
        param_standard = self.dlg.param_standard.value()
        param_radius = self.dlg.param_radius.value()
        curvature_method = self.get_curvature_method(mode, self.dlg.curvature_box.currentText())

        csmap_maker = CSMapMake(self.iface)

        if self.csmap_process == self.csmap_batch_process:
            input_dir = self.dlg.input_folder_edit.text()
            if len(input_dir) == 0:
                pal = self.dlg.input_folder_edit.palette()
                pal.setColor(QPalette.Base, QColor("pink"))
                self.dlg.input_folder_edit.setPalette(pal)
                return
            
            output_dir = self.dlg.output_folder_edit.text()
            if len(output_dir) == 0:
                pal = self.dlg.output_folder_edit.palette()
                pal.setColor(QPalette.Base, QColor("pink"))
                self.dlg.output_folder_edit.setPalette(pal)
                return

            for f in os.listdir(input_dir):
                r,e = os.path.splitext(f)
                if e.lower() not in (".tif", ".tiff", ".las"):
                    continue
										
                if e.lower() == ".las":
                    input_file = self._convert_las_to_tiff(input_dir, f)
                    if input_file is None:
                        continue
                else:
                    input_file = input_dir+"/"+f

                csmap_maker.csmapMake(input_file, curvature_method, [param_standard, param_radius], True, output_dir, True)
                csmap_maker.clearLayers()

            if self.dlg.load_flg.isChecked():
                csmap_maker.loadResultFiles()

        elif self.csmap_process == self.csmap_single_process:
            layer = self.dlg.demlayer_box.currentLayer()
            if layer is None:
                return

            csmap_maker.csmapMake(layer, curvature_method, [param_standard, param_radius])

    def get_curvature_method(self, mode, ctext):
        #Plan+General Mode
        if mode == -3:
            curvature_method = ['C_PLAN', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_GENE', 'RdBu', 5, True, 0.5, -0.326, 0.48]
        # mode == -2 CS-MAP Mode
        else:
            if ctext == 'General Curvature':
                curvature_method = ['C_GENE', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_GENE', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Profile Curvature':
                curvature_method = ['C_PROF', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_PROF', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Plan Curvature':
                curvature_method = ['C_PLAN', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_PLAN', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Tangential Curvature':
                curvature_method = ['C_TANG', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_TANG', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Longitudinal Curvature':
                curvature_method = ['C_LONG', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_LONG', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Cross-Sectional Curvature':
                curvature_method = ['C_CROS', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_CROS', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Minimal Curvature':
                curvature_method = ['C_MINI', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_MINI', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Maximal Curvature':
                curvature_method = ['C_MAXI', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_MAXI', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Total Curvature':
                curvature_method = ['C_TOTA', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_TOTA', 'RdBu', 9, True, 0.5, -0.2, 0.2]
            elif ctext == 'Flow Line Curvature':
                curvature_method = ['C_ROTO', 'Blues', 9, True, 0.5, -0.2, 0.2, 'C_ROTO', 'RdBu', 9, True, 0.5, -0.2, 0.2]
        return curvature_method
			
    def _convert_las_to_tiff(self, dir, file):
        if self._check_lastools() == False:
            return None
				
        input_file = dir+"/"+file
        r,e = os.path.splitext(file)
				
        output_file = processing.getTempDirInTempFolder()+r'/'+r+r".tif"				
				
        processing.run("LAStools:las2dem", {
           "VERBOSE": True,
           "GUI":False,
           "STEP": 1.0,
           "INPUT_LASLAZ": input_file,
           "PRODUCT": 0,
           "ATTRIBUTE": 0,
           "OUTPUT_RASTER": output_file
          })
				
        return output_file
			
    def _check_lastools(self):
        flag = False
        for a in QgsApplication.processingRegistry().providers():
            if a.name() == "LAStools":
                flag = True
                break
        return flag