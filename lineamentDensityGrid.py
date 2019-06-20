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

To improve this program or group of programs please consult:

A. C. DineshVipin Joseph MarkoseKallesh Danappa JayappaKallesh Danappa Jayappa (2013)
Linfo – a visual basic program for lineament density, frequency and intersection density analysis
October 2013. Earth Science Informatics 7(3)

Thushan EkneligodaHerbert HenkelHerbert Henkel (2010)
Interactive spatial analysis of lineaments
Computers & Geosciences 36(8):1081-1090

Antonio M Casas, Angel L Cortés, Adolfo Maestro, M.Asunción Soriano, ... Javier Bernal (2000). 
LINDENS: A program for lineament length and density analysis
Computer & Geosciences 36: 1011-1022
"""

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink)
import processing


class lineamentDensityGrid(QgsProcessingAlgorithm):
    """


    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT  = 'INPUT'
    INPUT_CELLSIZE = 'Input_CellSize'
    OUTPUT = 'OUTPUT'
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return lineamentDensityGrid()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lineamentDensityGrid'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Lineament Density Grid')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Lineament Analysis')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'geoLineaments'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("A simple method for calculation of  a lineament density grid based on total lengths of lineaments inside of each cell")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorLine]
            )
        )
         
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_CELLSIZE, 
                self.tr("Input Cell Size"), 
                QgsProcessingParameterNumber.Double,
                1000
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Output Density Grid'),
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        feedback.pushInfo(source.sourceName())
        inputCrs = source.sourceCrs().authid()
        
        feedback.pushInfo('CRS: ' + inputCrs)
        
        xMin = str(source.sourceExtent().xMinimum())
        xMax = str(source.sourceExtent().xMaximum())
        yMin = str(source.sourceExtent().yMinimum())
        yMax = str(source.sourceExtent().yMaximum())
        
        sourceExtent = xMin +',' + xMax +',' + yMin +',' + yMax
        
        feedback.pushInfo(sourceExtent)

        cellSizeVal = self.parameterAsDouble(
            parameters,
            self.INPUT_CELLSIZE,
            context
        )
        
        outputFile = self.parameterAsOutputLayer(
            parameters,
            self.OUTPUT,
            context
        )
        
        
        vectorGrid = processing.run("qgis:creategrid", {
            'TYPE': 2,
            'EXTENT': sourceExtent,
            'HSPACING': str(cellSizeVal),
            'VSPACING': str(cellSizeVal),
            'HOVERLAY': 0,
            'VOVERLAY': 0,
            'CRS': inputCrs,
            'OUTPUT': 'memory:'
        })
        
        vectorIntersection = processing.run('qgis:intersection', {
            'INPUT': source.sourceName(),
            'OVERLAY': vectorGrid['OUTPUT'],
            'INPUT_FIELDS': '',
            'OVERLAY_FIELDS': '',
            'OUTPUT': 'memory:'
        })
        
        lineSegments = processing.run("qgis:fieldcalculator",{
            'INPUT': vectorIntersection['OUTPUT'],
            'FIELD_NAME': 'LineDensity',
            'FIELD_TYPE': 0,
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 0,
            'NEW_FIELD': 1,
            'FORMULA': '$length',
            'OUTPUT': 'memory:'
        
        })
        
        #free memory
        del(vectorIntersection)
        
        gridDensityFull = processing.run("qgis:joinattributesbylocation",{
            'INPUT': vectorGrid['OUTPUT'],
            'JOIN': lineSegments['OUTPUT'],
            'PREDICATE': 1,
            #'JOIN_FIELDS': 'lineLength',
            'METHOD': 0,
            'DISCARD_NONMATCHING':  1,
            #'PREFIX': 'd_',
            'OUTPUT': outputFile        
        })
        
 
        
        return {self.OUTPUT: 'OUTPUT'}
