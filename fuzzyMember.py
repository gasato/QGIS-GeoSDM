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
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterRasterDestination)
import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry



class fuzzyMember(QgsProcessingAlgorithm):
    """
   
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    INPUT_DOUBLE_1 = 'Input_First'
    INPUT_DOUBLE_2 = 'Input_Second'
    CHOICE_MFUNCTION  = 'Choice_MFunction'


    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return fuzzyMember()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'fuzzyMember'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Fuzzy Membership Functions')
        

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
        return self.tr("Calculation of degree of membership by different membership functions")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                self.tr('Input raster')
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.CHOICE_MFUNCTION, 
                self.tr("Select Membership Function"), 
                ['Linear+', 'Linear-', 'Sinusoidal+', 'Sinusoidal-', 'Gaussian']
            )
        )


        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_DOUBLE_1, 
                self.tr("Input First Threshold"), 
                QgsProcessingParameterNumber.Double
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_DOUBLE_2, 
                self.tr("Input Second Threshold or Standard D"), 
                QgsProcessingParameterNumber.Double
            )
        )


        self.addParameter(
            QgsProcessingParameterRasterDestination(
                self.OUTPUT,
                self.tr('Fuzzy Model')
            )
        )


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        rasterInput = self.parameterAsRasterLayer(
            parameters,
            self.INPUT,
            context
        )
        
        firstVal = self.parameterAsDouble(
            parameters,
            self.INPUT_DOUBLE_1,
            context
        )
        
        secondVal = self.parameterAsDouble(
            parameters,
            self.INPUT_DOUBLE_2,
            context
        )
        
        feedback.pushInfo('First Value : ' + str(firstVal))
        feedback.pushInfo('Second Value: ' + str(secondVal))
        
        mFunction = self.parameterAsEnum(parameters, self.CHOICE_MFUNCTION, context)
        feedback.pushInfo('Membership Function: ' + str(mFunction))
        
        outputFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        feedback.pushInfo('Output File: ' + outputFile)
        
        rCalcEntry        = QgsRasterCalculatorEntry()
        rCalcEntry.ref    = 'r1@1'
        rCalcEntry.raster = rasterInput
        
        l_plus  = '((r1@1 >= %s) AND (r1@1 <= %s)) * ((r1@1 -  %s) / (%s - %s))' % (firstVal, secondVal, firstVal, secondVal, firstVal)
        l_minus = '((r1@1 >= %s) AND (r1@1 <= %s)) * ((%s - r1@1 ) / (%s - %s))' % (firstVal, secondVal, secondVal, secondVal, firstVal)
        
        cos_plus = '((r1@1 >= %s) AND (r1@1 <= %s)) * ( 0.5 * ( 1 - cos( 3.141592 * (( r1@1 - %s ) / (%s - %s) ))))' % (firstVal, secondVal, firstVal, secondVal, firstVal)
                #No anda bien
        cos_minus= '((r1@1 >= %s) AND (r1@1 <= %s)) * ( 0.5 * ( 1 + cos( 3.141592 * (( r1@1 - %s ) / (%s - %s) ))))' % (firstVal, secondVal, firstVal, secondVal, firstVal)
        
        gaussf   = ' ( 2.7182818 ^ (( -1 * (r1@1 - %s ) ^ 2) / (2 * %s * %s) ))' % (firstVal, secondVal, secondVal)
        
        ceroOne = '(r1@1 < %s) * 0 + (r1@1 > %s) * 1' % (firstVal, secondVal)
        oneCero = '(r1@1 < %s) * 1 + (r1@1 > %s) * 0' % (firstVal, secondVal)
        ceroCero = '(r1@1 < %s) * 0 + (r1@1 > %s) * 0' % (firstVal, secondVal)

        if mFunction == 0:
            formula = l_plus + ' + ' + ceroOne
        elif mFunction == 1:
            formula = l_minus + ' + ' + oneCero
        elif mFunction == 2:
            formula = cos_plus + ' + ' + ceroOne
        elif mFunction == 3:
            formula = cos_minus + ' + ' + oneCero
        elif mFunction == 4:
            formula = gaussf 
        #formula = '(r1@1 < %s) * 0 + (r1@1 > %s) * 1 + (((r1@1 >= %s) AND (r1@1 <= %s)) * ((r1@1 -  %s) / (%s - %s)) ' % (firstVal, secondVal, firstVal, secondVal, firstVal, secondVal, firstVal )
        
        
        feedback.pushInfo('Formula: ' + str(formula))
        calc = QgsRasterCalculator(formula, outputFile, 'GTiff', rasterInput.extent(), rasterInput.width(), rasterInput.height(), [rCalcEntry])
        #calc = QgsRasterCalculator("r1@1", outputFile, 'GTiff', rasterInput.extent(), rasterInput.width(), rasterInput.height(), [rCalcEntry])
        
        feedback.pushInfo("p calc1")
        calc.processCalculation()
        feedback.pushInfo("p calc1")

        

        return {self.OUTPUT: outputFile}
        
