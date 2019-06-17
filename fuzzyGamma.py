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
                       QgsProcessingParameterMultipleLayers, 
                       QgsProcessingParameterRasterDestination)
import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry



class fuzzyGamma(QgsProcessingAlgorithm):
    """
   
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_1 = 'INPUT_1'
    INPUT_GAMMA = 'INPUT_GAMMA'
    OUTPUT = 'OUTPUT'

    


    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return fuzzyGamma()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'fuzzyGamma'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Fuzzy Gamma Operations')

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
        return self.tr("Fuzzy gamma operations between a list of raster layers with membership values")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.INPUT_1,
                self.tr('Input raster layers'),
                QgsProcessing.TypeRaster
            )
        )
        
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUT_GAMMA, 
                self.tr("Input Gamma [0:1]"), 
                QgsProcessingParameterNumber.Double,
                0,
                False,
                0,
                1
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
        rasterInputLst = self.parameterAsLayerList(
            parameters,
            self.INPUT_1,
            context
        )
        
        gammaVal = self.parameterAsDouble(
            parameters,
            self.INPUT_GAMMA,
            context
        )
        
        feedback.pushInfo('Gamma val: ' + str(gammaVal))
                
        outputFile = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        feedback.pushInfo('Output File: ' + outputFile)
        
        #Loop for calculation
        rEntriesLst = []
        cont      = 1
        fsum      = '1 - ('
        fMultiply = ''
        
        for r in rasterInputLst:
            rCalcEntry        = QgsRasterCalculatorEntry()
            rRefName          = 'r%s@1' % (str(cont))
            rCalcEntry.ref    = rRefName
            feedback.pushInfo(rCalcEntry.ref)
            rCalcEntry.raster = r
            rEntriesLst.append(rCalcEntry)
            feedback.pushInfo('Raster n: %s' % ( rRefName ))
            
            if cont != 1: fsum = fsum + '* ( 1 - %s )' % rRefName
            else: fsum = fsum + '( 1 - %s )' % rRefName
            
            if cont != 1: fMultiply = fMultiply + ' * ' + rRefName
            else: fMultiply = rRefName
            
            cont += 1
            
        fsum = fsum + ')'
        feedback.pushInfo(fsum)
        feedback.pushInfo(fMultiply)
        
        formula = '((' + fsum +') ^ ' + str(gammaVal) + ') *  ((' + fMultiply + ') ^ ( 1 - ' + str(gammaVal) + '))'
        feedback.pushInfo('Formula: ' + str(formula))
        
        rasterInput1=rasterInputLst[0]
        calc = QgsRasterCalculator(formula, outputFile, 'GTiff', rasterInput1.extent(), rasterInput1.width(), rasterInput1.height(), rEntriesLst)
        
        
        feedback.pushInfo("Doing calculation")
        calc.processCalculation()
        feedback.pushInfo("Calculation finished")
      
        return {self.OUTPUT: outputFile}
        
