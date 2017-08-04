# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CSMapDialog
                                 A QGIS plugin
 csmap plugin
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

import os

from PyQt4 import QtGui, uic
from csmap_dialog_base import Ui_CSMapDialogBase
#FORM_CLASS, _ = uic.loadUiType(os.path.join(
#    os.path.dirname(__file__), 'csmap_dialog_base.ui'))


class CSMapDialog(QtGui.QDialog, Ui_CSMapDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        super(CSMapDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def accept(self):
        pass

    def input_folder_action(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)

        if dialog.exec_():
            self.input_folder_edit.setText(dialog.selectedFiles()[0])
            pal = self.input_folder_edit.palette()
            pal.setColor(QtGui.QPalette.Base, QtGui.QColor("white"))
            self.input_folder_edit.setPalette(pal)

    def output_folder_action(self):
        dialog = QtGui.QFileDialog(self)
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)

        if dialog.exec_():
            self.output_folder_edit.setText(dialog.selectedFiles()[0])
            pal = self.output_folder_edit.palette()
            pal.setColor(QtGui.QPalette.Base, QtGui.QColor("white"))
            self.output_folder_edit.setPalette(pal)
