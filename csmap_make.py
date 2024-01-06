from builtins import str
from builtins import range
from builtins import object
import os
from qgis.PyQt import QtCore, QtGui
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from osgeo import gdal, osr
import processing
import tempfile
import uuid

from qgis.PyQt.QtWidgets import QMessageBox

class CSMapMake(object):
    def __init__(self, iface, progressBar):
        self.iface = iface
        self.progressBar = progressBar
        self.result_files = []
        self.temp_layers = []

    def clearLayers(self):
        for l in self.temp_layers:
            QgsProject.instance().removeMapLayer(l)
        self.temp_layers = []

    def loadResultFiles(self):
        for r in self.result_files:
            self.iface.addRasterLayer(r, r)
        
    def _getTempFileName(self, file_name):
        # processing.getTempDirInTempFolder() was removed in QGIS 3.26
        # https://github.com/qgis/QGIS/commit/b752d561862a7769f6c1c8122607611382ba9b0d
        # Add code that was defined in the deleted function.
        # https://github.com/waigania13/CSMapMaker/issues/9
        dir_name = QgsProcessingUtils.tempFolder()
        dir_name = os.path.join(dir_name, uuid.uuid4().hex)
        os.makedirs(dir_name.strip('\n\r '), exist_ok=True)
        return dir_name+r'/'+file_name

    def csmapMake(self, dem, curvature_method, gaussian_params, progress_val, progress_step, to_file=False, outdir=None, batch_mode=False):
        if type(dem) is str:
            dem_layer = QgsRasterLayer(dem, "DEM")
            QgsProject.instance().addMapLayer(dem_layer, False)
            self.temp_layers.append(dem_layer)
        else:
            dem_layer = dem

        options = {"ELEVATION":dem_layer, "METHOD":6, "UNIT_SLOPE":0, "UNIT_ASPECT":0, "SLOPE":self._getTempFileName("SLOPE.sdat"), "ASPECT":self._getTempFileName("ASPECT.sdat"), "C_GENE":self._getTempFileName("C_GENE.sdat"), "C_PLAN":self._getTempFileName("C_PLAN.sdat"), "C_PROF":self._getTempFileName("C_PROF.sdat"), "C_TANG":self._getTempFileName("C_TANG.sdat"), "C_LONG":self._getTempFileName("C_LONG.sdat"), "C_CROS":self._getTempFileName("C_CROS.sdat"), "C_MINI":self._getTempFileName("C_MINI.sdat"), "C_MAXI":self._getTempFileName("C_MAXI.sdat"), "C_TOTA":self._getTempFileName("C_TOTA.sdat"), "C_ROTO":self._getTempFileName("C_ROTO.sdat")}
        dem_result = processing.run("saga:slopeaspectcurvature", options, feedback= QgsProcessingFeedback())
				
        QtCore.QCoreApplication.processEvents() 
        progress_val = progress_val + progress_step
        self.progressBar.setValue(progress_val)

        gaussian = processing.run("saga:gaussianfilter", {"INPUT":dem_layer, "SIGMA":gaussian_params[0], "MODE":1, "RADIUS":gaussian_params[1], "RESULT":self._getTempFileName("RESULT.sdat")}, feedback= QgsProcessingFeedback())
				
        QtCore.QCoreApplication.processEvents() 
        progress_val = progress_val + progress_step
        self.progressBar.setValue(progress_val)

        options = {"ELEVATION":QgsRasterLayer(gaussian["RESULT"]), "METHOD":6, "UNIT_SLOPE":0, "UNIT_ASPECT":0, "SLOPE":self._getTempFileName("SLOPE.sdat"), "ASPECT":self._getTempFileName("ASPECT.sdat"), "C_GENE":self._getTempFileName("C_GENE.sdat"), "C_PLAN":self._getTempFileName("C_PLAN.sdat"), "C_PROF":self._getTempFileName("C_PROF.sdat"), "C_TANG":self._getTempFileName("C_TANG.sdat"), "C_LONG":self._getTempFileName("C_LONG.sdat"), "C_CROS":self._getTempFileName("C_CROS.sdat"), "C_MINI":self._getTempFileName("C_MINI.sdat"), "C_MAXI":self._getTempFileName("C_MAXI.sdat"), "C_TOTA":self._getTempFileName("C_TOTA.sdat"), "C_ROTO":self._getTempFileName("C_ROTO.sdat")}
        result = processing.run("saga:slopeaspectcurvature", options, feedback= QgsProcessingFeedback()) 
				
        QtCore.QCoreApplication.processEvents() 
        progress_val = progress_val + progress_step
        self.progressBar.setValue(progress_val)

        gaussian_layer = self.iface.addRasterLayer(gaussian["RESULT"], "GAUSSIAN_RESULT")
        self.temp_layers.append(gaussian_layer)
        QgsProject.instance().layerTreeRoot().findLayer(gaussian_layer).setItemVisibilityChecked(False)

        curvature_layer = self.iface.addRasterLayer(result[curvature_method[0]], curvature_method[0])
        self.temp_layers.append(curvature_layer)

        slope_layer = self.iface.addRasterLayer(dem_result["SLOPE"], "SLOPE")
        self.temp_layers.append(slope_layer)

        curvature_layer2 = self.iface.addRasterLayer(result[curvature_method[7]], curvature_method[7])
        self.temp_layers.append(curvature_layer2)

        slope_layer2 = self.iface.addRasterLayer(dem_result["SLOPE"], "SLOPE")
        self.temp_layers.append(slope_layer2)

        self._setLayerStyle(curvature_layer, 
            curvature_method[1],
            curvature_method[2],
            curvature_method[3],
            curvature_method[4],
            curvature_method[5],
            curvature_method[6])
        self._setLayerStyle(curvature_layer2, 
            curvature_method[8],
            curvature_method[9],
            curvature_method[10],
            curvature_method[11],
            curvature_method[12],
            curvature_method[13])
        if batch_mode:
            self._setLayerStyle(slope_layer, "Oranges", 9, False, 0.5, 0.0, 1.58)
            self._setLayerStyle(slope_layer2, "WhiteToBlack", 2, False, 0.5, 0.0, 1.58)
        else:
            self._setLayerStyle(slope_layer, "Oranges", 9, False, 0.5)
            self._setLayerStyle(slope_layer2, "WhiteToBlack", 2, False, 0.5)

        if to_file and outdir is not None:
            self._csmapToFile(dem_layer, [slope_layer2, curvature_layer2, slope_layer, curvature_layer, dem_layer], outdir)
        return progress_val

    def _setLayerStyle(self, layer, color_name, rank, reverse, opa=1.0, min=None, max=None):
        if min is None or max is None:
            data = gdal.Open(layer.dataProvider().dataSourceUri())
            band = data.GetRasterBand(1)
            (min,max) = band.ComputeRasterMinMax(1)
    
        sa = (max - min)/rank
    
        if color_name == 'WhiteToBlack':
            lst =  [ QgsColorRampShader.ColorRampItem(min, QtGui.QColor(255,255,255), str(round(min,3))), QgsColorRampShader.ColorRampItem(max, QtGui.QColor(0,0,0), str(round(max,3))) ]
        else :
            lst = []
            for i in range(rank):
                idx = rank-1-i if reverse else i
                lst.append(QgsColorRampShader.ColorRampItem(min+sa*i, QgsColorBrewerPalette.listSchemeColors(color_name, rank)[idx], str(round(min+sa*i,3))))
    
        myRasterShader = QgsRasterShader()
        myColorRamp = QgsColorRampShader()

        myColorRamp.setColorRampItemList(lst)
        myColorRamp.setColorRampType(QgsColorRampShader.Interpolated)
        myRasterShader.setRasterShaderFunction(myColorRamp)

        myPseudoRenderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), layer.type(),  myRasterShader)

        layer.setRenderer(myPseudoRenderer)
        layer.renderer().setOpacity(opa)

    def _csmapToFile(self, dem, layer_set, outdir): 

        if dem.rasterUnitsPerPixelX() == dem.rasterUnitsPerPixelY():
            dx = dem.rasterUnitsPerPixelX()
            dy = dem.rasterUnitsPerPixelY()
            w = dem.dataProvider().xSize()
            h = dem.dataProvider().ySize()
        elif dem.rasterUnitsPerPixelX() > dem.rasterUnitsPerPixelY():
            dx = dem.rasterUnitsPerPixelY()
            dy = dem.rasterUnitsPerPixelY()
            w = int(dem.dataProvider().xSize() * (dem.rasterUnitsPerPixelX() / dem.rasterUnitsPerPixelY()))
            h = dem.dataProvider().ySize()
        else:
            dx = dem.rasterUnitsPerPixelX()
            dy = dem.rasterUnitsPerPixelX()
            w = dem.dataProvider().xSize()
            h = int(dem.dataProvider().ySize() * (dem.rasterUnitsPerPixelY() / dem.rasterUnitsPerPixelX()))

        img = QtGui.QImage(QtCore.QSize(w, h), QtGui.QImage.Format_ARGB32_Premultiplied)
        color = QtGui.QColor(255, 255, 255)
        img.fill(color.rgb())

        setting = QgsMapSettings()
        setting.setExtent(dem.dataProvider().extent())
        setting.setDestinationCrs(dem.crs())
        setting.setOutputSize(QtCore.QSize(w, h))
        setting.setLayers(layer_set)
        setting.updateDerived()

        p = QtGui.QPainter()
        p.begin(img)

        render = QgsMapRendererCustomPainterJob(setting, p)

        render.start()
        render.waitForFinished()

        p.end()

        temp = tempfile.NamedTemporaryFile()
        img.save(temp.name+".tif","tif")

        src_ds = gdal.Open(temp.name+".tif")
        driver = gdal.GetDriverByName("GTiff")

        filepath, filename = os.path.split(str(dem.dataProvider().dataSourceUri()))

        dst_file = outdir+r"/csmap_"+filename
        dst_ds = driver.CreateCopy(dst_file, src_ds, 0)
        geo_trans = [dem.dataProvider().extent().xMinimum(), dx, 0, dem.dataProvider().extent().yMaximum(), 0, dy*-1]
        dst_ds.SetGeoTransform(geo_trans)
        dst_ds.SetProjection(str(dem.crs().toWkt()))

        dst_ds = None
        src_ds = None
        temp.close()

        self.result_files.append(dst_file)
