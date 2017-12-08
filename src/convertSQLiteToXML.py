'''
Created on Dec 7, 2017

@author: Hovanes Egiyan
'''
import sys, string, getopt, os
from optparse import OptionParser

from copy import deepcopy
import lxml.etree

from beastComponentFromSQLite import beastComponentFromSQLite
from sqliteDB import sqliteDB
from subsystem import subsystem


#===============================================================================
# Class to handle command line options
#===============================================================================
class clfOptions:
    """ Class to handle command line options  """
        
    # Constructor
    def __init__( self, argList ):
        self.optionDict = {}
        # Command line
        try:
            # Get options from command line
            self.parseCommandLine( argList )  
        except getopt.GetoptError as errMsg:
            print errMsg
            self.printHelpMessage()
            sys.exit(-1)
        return
    
    
    # Parse command file and append the option list extracted from the command file
    def parseCommandLine( self, argList ):
        print "Starting command line parsing:", argList
        # Here I am using optparse module which may be obsolete in future Python versions 
        # This part might need to be redone for it to work with Python 3.1
        # Python does not seem to be forward or backward compatable
        parser = OptionParser(usage = "usage: %prog [options] ")
        parser.add_option( "-s", "--sql", 
                           action="store", dest="sql", type="string", metavar="SQLiteFile", 
                           default="tt.db", help="Define SQLiteFile" )
        parser.add_option( "-x", "--xml", 
                           action="store", dest="xml", type="string", metavar="XMLFile", 
                           default="tt.xml", help="Define file name for output XML file" )
        
        (opts, args) = parser.parse_args( argList )
        
        # Assign the elements of the dictionary to the parsed option values
        self.optionDict["SQLiteFile"]   = opts.sql
        self.optionDict["XMLFile"]      = opts.xml
        return
        
        
       
    # Return option for key optKey if exists, otherwise return None
    def getOption(self, optKey):
        if optKey in self.optionDict:
            return self.optionDict[optKey]
        else :
            return None


    # Returns the dictionary of all options
    def getOptions(self):
        return self.optionDict


if __name__ == '__main__':
    print "Here we go"

    globOptions = clfOptions( sys.argv[1:] )

    # Get the global options from the clfOptions class
    progOpts = globOptions
    
    sqlObject = sqliteDB( progOpts.getOption("SQLiteFile") )
    
    detMap = sqlObject.getDetectors()
    newElement = lxml.etree.Element( "config", name = "HallD" )
    newElementTree = lxml.etree.ElementTree( newElement)
    for detName in detMap.keys() :
        print "Doing detector called ", detName
        detID = detMap[detName]["id"]
        detSubsystem = subsystem( sqlObject.curs, detID)
        sqlComp = beastComponentFromSQLite( detSubsystem )
        detElement = sqlComp.makeXMLElement( newElement )

    # write the old tree into a new file
    outFile = open( progOpts.getOption("XMLFile"), 'w' )          # Open the file for writing
    newElementTree.write( outFile, pretty_print=True )
    outFile.close()
    
    