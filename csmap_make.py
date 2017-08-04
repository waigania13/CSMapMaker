import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import *
from osgeo import gdal, osr
import processing
import tempfile

class CSMapMake:
    def __init__(self, iface):
        self.iface = iface
        self.result_files = []
        self.temp_layers = []

    def clearLayers(self):
        for l in self.temp_layers:
            QgsMapLayerRegistry.instance().removeMapLayer(l)
        self.temp_layers = []

    def loadResultFiles(self):
        for r in self.result_files:
            processing.load(r)
        
    def csmapMake(self, dem, curvature_method, gaussian_params, to_file=False, outdir=None, batch_mode=False):
        if type(dem) == str or type(dem) == unicode:
            dem_layer = processing.load(dem)
            self.temp_layers.append(dem_layer)
        else:
            dem_layer = dem

        dem_result = processing.runalg("saga:slopeaspectcurvature", dem_layer,  6, 0, 0, None, None, None, None, None, None,None, None, None, None, None, None)

        gaussian = processing.runalg("saga:gaussianfilter", dem, gaussian_params[0], 1, gaussian_params[1], None)
        result = processing.runalg("saga:slopeaspectcurvature", gaussian["RESULT"],  6, 0, 0, None, None, None, None, None, None,None, None, None, None, None, None)

        legend = self.iface.legendInterface()

        gaussian_layer = processing.load(gaussian["RESULT"])
        self.temp_layers.append(gaussian_layer)
        legend.setLayerVisible(gaussian_layer, False)

        curvature_layer = processing.load(result[curvature_method[0]])
        self.temp_layers.append(curvature_layer)

        slope_layer = processing.load(dem_result["SLOPE"])
        self.temp_layers.append(slope_layer)

        curvature_layer2 = processing.load(result[curvature_method[7]])
        self.temp_layers.append(curvature_layer2)

        slope_layer2 = processing.load(dem_result["SLOPE"])
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
            self._csmapToFile(dem_layer, [slope_layer2.id(), curvature_layer2.id(), slope_layer.id(), curvature_layer.id(), dem_layer.id()], outdir)

    def _setLayerStyle(self, layer, color_name, rank, reverse, opa=1.0, min=None, max=None):
        if min is None or max is None:
            data = gdal.Open(layer.dataProvider().dataSourceUri())
            band = data.GetRasterBand(1)
            (min,max) = band.ComputeRasterMinMax(1)
    
        sa = (max - min)/rank
    
        if color_name == 'WhiteToBlack':
            lst =  [ QgsColorRampShader.ColorRampItem(min, QColor(255,255,255), str(round(min,3))), QgsColorRampShader.ColorRampItem(max, QColor(0,0,0), str(round(max,3))) ]
        else :
            lst = []
            for i in range(rank):
                idx = rank-1-i if reverse else i
                lst.append(QgsColorRampShader.ColorRampItem(min+sa*i, QgsColorBrewerPalette.listSchemeColors(color_name, rank)[idx], str(round(min+sa*i,3))))
    
        myRasterShader = QgsRasterShader()
        myColorRamp = QgsColorRampShader()

        myColorRamp.setColorRampItemList(lst)
        myColorRamp.setColorRampType(QgsColorRampShader.INTERPOLATED)
        myRasterShader.setRasterShaderFunction(myColorRamp)

        myPseudoRenderer = QgsSingleBandPseudoColorRenderer(layer.dataProvider(), layer.type(),  myRasterShader)

        layer.setRenderer(myPseudoRenderer)
        layer.renderer().setOpacity(opa)

        layer.triggerRepaint()
        self.iface.legendInterface().refreshLayerSymbology(layer)

    def _csmapToFile(self, dem, layer_set, outdir): 
        dp = dem.dataProvider()
        img = QImage(QSize(dp.xSize(), dp.ySize()), QImage.Format_ARGB32_Premultiplied)
        color = QColor(255, 255, 255)
        img.fill(color.rgb())

        p = QPainter()
        p.begin(img)

        render = QgsMapRenderer()
        render.setDestinationCrs(dem.crs())
        render.setProjectionsEnabled(True)

        render.setLayerSet(layer_set)

        rect = QgsRectangle(render.fullExtent())
        render.setExtent(rect)

        render.setOutputSize(img.size(), img.logicalDpiX())
        render.render(p)

        p.end()

        temp = tempfile.NamedTemporaryFile()
        img.save(temp.name+".tif","tif")

        src_ds = gdal.Open(temp.name+".tif")
        driver = gdal.GetDriverByName("GTiff")

        filepath, filename = os.path.split(str(dp.dataSourceUri()))

        dst_file = outdir+r"/csmap_"+filename
        dst_ds = driver.CreateCopy(dst_file, src_ds, 0)
        geo_trans = [rect.xMinimum(), dem.rasterUnitsPerPixelX(), 0, rect.yMaximum(), 0, dem.rasterUnitsPerPixelY()*-1]
        dst_ds.SetGeoTransform(geo_trans)
        dst_ds.SetProjection(str(dem.crs().toWkt()))

        dst_ds = None
        src_ds = None
        temp.close()

        self.result_files.append(dst_file)
