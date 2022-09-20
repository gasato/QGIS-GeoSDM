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


class lineamentParamCalc(QgsProcessingAlgorithm):
    """


    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT  = 'INPUT'
    OUTPUT = 'OUTPUT'
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return lineamentParamCalc()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lineamentParamCalc'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Lineament Parameters Calculation')

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
        return self.tr("Calculation of lineame length, azimuth and orientation by cardinal points")

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
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Output Lineament Layer'),
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
        
        inputCrs = source.sourceCrs().authid()
        
        feedback.pushInfo('CRS: ' + inputCrs)
      
        outputFile = self.parameterAsOutputLayer(
            parameters,
            self.OUTPUT,
            context
        )
        
       
        lineCalcutation1 = processing.run("qgis:fieldcalculator",{
            'INPUT': source.sourceName(),
            'FIELD_NAME': 'length',
            'FIELD_TYPE': 0,
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 0,
            'NEW_FIELD': 1,
            'FORMULA': '$length',
            'OUTPUT': 'memory:'
        })
        
        
        lineCalcutation2 = processing.run("qgis:fieldcalculator",{
            'INPUT': lineCalcutation1['OUTPUT'],
            'FIELD_NAME': 'azimuth',
            'FIELD_TYPE': 0,
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 0,
            'NEW_FIELD': 1,
            'FORMULA': 'degrees(azimuth(start_point($geometry), end_point($geometry)))',
            'OUTPUT': 'memory:'
        })
 
    
        f = 'CASE\n'
        f = f + 'when ((0 <= azimuth) and (azimuth <= 22.5)) or ((157.5 <= azimuth) and ( azimuth <= 202.5)) or ((337.5 <= azimuth) and (azimuth <= 360)) then \'N-S\'\n' 
        f = f + 'when ((22.5 <= azimuth) and ( azimuth <= 67.5)) or ((202.5 <= azimuth) and (azimuth <= 247.5)) then \'NE-SW\'\n'
        f = f + 'when ((67.5 <= azimuth) and ( azimuth <= 112.5)) or ((247.5 <= azimuth) and (azimuth <= 292.5)) then \'E-W\'\n' 
        f = f + 'when ((112.5 <= azimuth) and ( azimuth <= 157.5)) or ((292.5 <= azimuth) and ( azimuth <= 337.5)) then \'NW-SE\'\n' 
        f = f + 'END'
    
        lineCalcutation3 = processing.run("qgis:fieldcalculator",{
            'INPUT': lineCalcutation2['OUTPUT'],
            'FIELD_NAME': 'orientation',
            'FIELD_TYPE': 2,
            'FIELD_LENGTH': 10,
            'FIELD_PRECISION': 0,
            'NEW_FIELD': 1,
            'FORMULA': f,
            'OUTPUT': outputFile #'memory:'
        })
 

 
        
        return {self.OUTPUT: 'OUTPUT'}
