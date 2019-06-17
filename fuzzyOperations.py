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
__date__ = 'June 2019'

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterLayer,  
                       QgsProcessingParameterRasterDestination)
import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry



class fuzzyOperations(QgsProcessingAlgorithm):
    """
   
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_1 = 'INPUT_1'
    INPUT_2 = 'INPUT_2'
    OUTPUT = 'OUTPUT'
    CHOICE_FOPERATION = 'Choice_FOperation'
    


    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return fuzzyOperations()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'fuzzyOperations'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Fuzzy Operations')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Fuzzy')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'fuzzy'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("Fuzzy operations between two raster with membership values")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_1,
                self.tr('Input raster 1')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_2,
                self.tr('Input raster 2')
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.CHOICE_FOPERATION, 
                self.tr("Select Fuzzy Operation"), 
                ['Sum', 'AND', 'OR', 'Multiply']
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
        rasterInput1 = self.parameterAsRasterLayer(
            parameters,
            self.INPUT_1,
            context
        )
        
        rasterInput2 = self.parameterAsRasterLayer(
            parameters,
            self.INPUT_2,
            context
        )
        
        FOperation = self.parameterAsEnum(parameters, self.CHOICE_FOPERATION, context)
        feedback.pushInfo('Fuzzy Operation: ' + str(FOperation))
        
        outputFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        feedback.pushInfo('Output File: ' + outputFile)
        
        rCalcEntry1        = QgsRasterCalculatorEntry()
        rCalcEntry1.ref    = 'r1@1'
        rCalcEntry1.raster = rasterInput1
        
        rCalcEntry2        = QgsRasterCalculatorEntry()
        rCalcEntry2.ref    = 'r2@1'
        rCalcEntry2.raster = rasterInput2
        
        
        fsum  = '1 - (( 1 - r1@1) * (1 - r2@1))'
        fAnd  = '((r1@1 < r2@1) * r1@1 ) + ((r2@1 < r1@1) * r2@1 ) + ((r2@1 = r1@1) * r2@1 ) '
        fOr   = '((r1@1 > r2@1) * r1@1 ) + ((r2@1 > r1@1) * r2@1 ) + ((r2@1 = r1@1) * r2@1 )' 
        fMultiply = 'r1@1 * r2@1'

        if FOperation == 0:
            formula = fsum
        elif FOperation == 1:
            formula = fAnd
        elif FOperation == 2:
            formula = fOr
        elif FOperation == 3:
            formula = fMultiply
        
        feedback.pushInfo('Operator: ' + str(FOperation))
        feedback.pushInfo('Formula: ' + str(formula))
        calc = QgsRasterCalculator(formula, outputFile, 'GTiff', rasterInput1.extent(), rasterInput1.width(), rasterInput1.height(), [rCalcEntry1, rCalcEntry2])
        
        
        feedback.pushInfo("p calc1")
        calc.processCalculation()
        feedback.pushInfo("p calc1")
      
        return {self.OUTPUT: outputFile}
        
