# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************

Script developed based on Wolfgang Kainz, University of Vienna, Austria
https://homepage.univie.ac.at/wolfgang.kainz/Lehrveranstaltungen/ESRI_Fuzzy_Logic/File_2_Kainz_Text.pdf

toDo:
Membership function graphics with R

"""

__author__ = 'Carlos Gabriel Asato'
__date__   = 'June 2019'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterDistance,
                       QgsProcessingParameterExtent,  
                       QgsProcessingParameterMultipleLayers, 
                       QgsProcessingParameterRasterDestination)
import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis.core import QgsRasterLayer


class oBooleanOverlayVector2Raster(QgsProcessingAlgorithm):
    """
   
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_LST   = 'INPUT_LST'
    CELL_SIZE   = 'CELL_SIZE'
    EXTENT_AREA = 'EXTENT_AREA'
    CRS         = 'CRS'
    OUTPUT      = 'OUTPUT'

    


    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return oBooleanOverlayVector2Raster()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'oBooleanOverlayVector2Raster'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Boolean Overlay - Vector to Raster')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Overlay Analysis')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Overlay Analysis'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Boolean overlay analysis. Inputs are vectorial layers, output a raster")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_LST,
                self.tr('Input vector layers'),
                QgsProcessing.TypeVector
            )
        )
        self.addParameter(
            QgsProcessingParameterDistance(
                self.CELL_SIZE,
                self.tr('Cell Size'), 
                1000, 
                'INPUT_LST', 
                1, 
                0
            )
        ) 
 
        self.addParameter(
            QgsProcessingParameterExtent(
                self.EXTENT_AREA, 
                self.tr("Input Extent"),
            )
        )

        
        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT, 
                self.tr("Output")
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        vectorInputLst = self.parameterAsLayerList(
            parameters,
            self.INPUT_LST,
            context
        )
        
        cellSize = self.parameterAsDouble(parameters, self.CELL_SIZE, context)
        
        extentArea = self.parameterAsExtent(parameters, self.EXTENT_AREA, context ) #, crs)
        
    
        outputFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        feedback.pushInfo('Output File: ' + outputFile)
        
        #Loop for calculation
        rasterDict = {}
        rEntriesLst = []
        cont      = 1        
        
        for V in vectorInputLst:
            r = processing.run('gdal:rasterize',{
                'INPUT': V,
                'BURN': 1,
                'UNITS': 1,
                'WIDTH': cellSize,
                'HEIGHT': cellSize,
                'EXTENT': extentArea,
                'DATA_TYPE': 0,
                'OUTPUT': 'memory:' 
            })
            
            feedback.pushInfo('Entry: ' + r['OUTPUT'])
            
            rName = 'raster' + str(cont) + '@1'
 
            rasterDict[rName]        = QgsRasterCalculatorEntry()
            rasterDict[rName].ref    = rName
            rasterDict[rName].raster = QgsRasterLayer(r['OUTPUT'])
            
            rEntriesLst.append(rasterDict[rName])         
           
            if cont != 1: fsum = fsum + ' + ' + rName
            else: fsum = rName

            cont += 1
            
        
        feedback.pushInfo('lst: ' + str(rEntriesLst))
        
        
        feedback.pushInfo('Formula: ' + str(fsum))
        
        if len(rEntriesLst) > 1:
            calc = QgsRasterCalculator(fsum, outputFile, 'GTiff', extentArea, extentArea.width(), extentArea.height(), rEntriesLst)
            feedback.pushInfo("Doing calculation")
            calc.processCalculation()
            feedback.pushInfo("Calculation finished")
        else:
            outputFile = rEntriesLst[0].raster

        return {self.OUTPUT: outputFile}
        
