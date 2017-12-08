#!/usr/bin/env python
''' 
Created on August 10, 2014
@author: Hovanes Egiyan
'''
#import _mysql
import os
import sys

from beastComponentFromSQLite import beastComponentFromSQLite
#from beastComponentInDB import beastComponentInDB
import sqlite3 as lite
from subsystem import subsystem


class sqliteDB(object):
    '''
    Class to handle direct accesses to BEAST alarm systems MySQL DB
    '''

    def __init__(self, dbFileName):
        '''
        Open the connection to the DB or 
        throw an exception in case of failure 
        '''

        # Define data members for this class 
        self.fileName = dbFileName  # Filename to get the SQLite DB
        self.con = None  # MySQL connector
        self.cur = None  # MySQL cursor
        
        # Connect to SQLite DB file with the detector configuration
        # This block would have to be changed when changing to MySQL DB
        if(not os.path.exists(self.fileName)):
            print "Cannot find the file <{0}>. Exiting...".format(self.fileName)
            sys.exit(-1)
            
        self.con = lite.connect(self.fileName)
        self.con.row_factory = lite.Row
        self.curs = self.con.cursor()
        return
    


       
                      

    def getDetectors(self) :
        """
        Find the existing configurations in the BEAST MySQL database and 
        return a list of configuration names 
        """
        self.curs.execute( "SELECT * FROM detector_hierarchy WHERE parent_id IS NULL" )
        detRows = self.curs.fetchall()
        retMap = {}
        for detector in detRows :
            print detector
            retMap[detector["name"]] = detector
        return retMap
        

if __name__ == '__main__':    
    args = sys.argv[1:]
    testObject = sqliteDB( "../tt.db")
#    print "Component ID for BCAL is ", testObject.getDetectorID("BCAL")
    detMap = testObject.getDetectors()
    print "Here we go"
#     for key in detMap :
#         print "id for ", key , " is " , detMap[key]["id"]    
    
#     for detName in detMap.keys() :
#         print "Working on ", detName 
#         try:
#             detSqlID = detMap[detName]["id"]
#             # create an object of subsystem type for this detector (AREA)
#             print "Creating subsystem for ", detName 
#             subDetector = subsystem(testObject.curs, detSqlID)
# #            print subDetector
#             print "Creating component for ", detName 
#             beastComp = beastComponentFromSQLite( subDetector )
#             print beastComp
#         except Exception as err:
#             print err
#             sys.exit(-1)
    psID = detMap["PS"]["id"]
    psSubsystem = subsystem(testObject.curs, psID)
    psComponent =  beastComponentFromSQLite( psSubsystem )
    print psComponent
    
    
    print "Done"

                
