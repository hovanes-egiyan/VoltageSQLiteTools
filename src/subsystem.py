'''
Created on October 7, 2013

This file contains a class to handle the detector hierarchy tree 
that describes the GlueX detector channel assignments. This class expected 
to be used for building MySQL database for the BEAST alarm system.  

@author: Hovanes Egiyan
'''

import os
import sys

from namedAlarmComponent import namedAlarmComponent
import sqlite3 as lite


#from beastFile import beastFile
class subsystem(namedAlarmComponent):
    '''
    Class to handle a node in the detector hierarchy 
    '''
    
    # Prefix for the EPICS PV variables
#    pvPrefix = "cj"
    pvPrefix = ""

    def __init__(self, inCursor=None, sqlDetID=None, parent=None):
        '''
        Constructor for the class. Creates the object, then to create objects for the children.
        That function will call the constructor for children, so the process will go recursively. 
        '''
        namedAlarmComponent.__init__(self, None, parent)
        self.id         = None      # id in the detector hierarchy DB
        self.parent_id  = None      # paprent_id in the detector hierarchy tree
#         self.name       = None      # name in the detector hierarchy tree 
        self.type       = None      # type in the detector hierarchy tree
        self.chanid     = None      # chanid in the detector hierarchy tree
        self.mtime      = None      # mtime (modification time) in the detector hierarchy tree
        
        self.curs       = inCursor  # cursor for the DB connector 
#         self.children   = []        # A list with the children of this object taken from the detector hierarchy DB
#         self.parentSys  = parent    # Reference to the parent object of the same class as self
        self.beastID    = None      # id that will correspond to this element in the MySQL DB for BEAST
        
        # Find the fields for this detector element to assign the data members
        self.curs.execute( "SELECT * FROM detector_hierarchy WHERE id=?", (sqlDetID,) )
        allDetectors = self.curs.fetchall()
        
        # Raise an exception if there are too many rows from the previous SQL 
        # There has to be only one entry in the table for each unique id
        if( len( allDetectors ) > 1 ):
            errMsg = "Too many detectors with id {0}, to be exact there are {1}".format(sqlDetID, len(allDetectors) )
            print errMsg
            raise Exception( errMsg )
        
        # Find the first detector_hierarchy raw in the DB 
        detector = allDetectors[0]
#        print "Creating a detector with {0} elements and id {1}".format(len(detector), sqlDetID)
#        (self.id, self.parent_id, self.name, self.type,  self.chanid, dummy) = detector
        self.id         = detector["id"]
        self.parent_id  = detector["parent_id"]
        self.name       = detector["name"]
        self.type       = detector["type"]
        self.chanid     = detector["chanid"]
        self.mtime      = detector["mtime"]
        
        # If cannot find the requested detector in the DB then raise an exception 
        if( self.id == 0 ) :
            errMsg = "Bad detector hierarchy <{0}>".format( sqlDetID )
            print errMsg
            raise Exception( errMsg )
 
        # Keep going to find the children
        self.children   = self.findChildren()
        if( len(self.children) == 0 ) :
            self.name = self.name + ":alarm"
        return
        
    
    def __str__(self):
        retString = "\nSubsystem with id {0}, parent {1}, name {2}, type {3}, chanid {4}".format(self.id, self.parent_id, self.name, self.type, self.chanid )
        if( len(self.children)>0 ) : 
            retString += "\nChildren are "       
        for child in self.children:
            retString += str(child)
        retString += "\nFull path is " + self.getFullName("->") + " pvName is " + self.getAlarmPVName()
        return retString
        
    def __repr__(self):
        retString = "\nSubsystem with id {0}, parent {1}, name {2}, type {3}, chanid {4}".format(self.id, self.parent_id, self.name, self.type, self.chanid )
        if( len(self.children)>0 ) : 
            retString += "\nChildren are "
        for child in self.children:
            retString += str(child)
        retString += "\nFull path is " + self.getFullName("->") + " pvName is " + self.getAlarmPVName()
        return retString
        
                
    def findChildren(self):
        """Finds children of this detector. Note that this function will create other 
        objects of this class which will in turn call this function. The recursive process 
        continues until we reach an object with no children found and the functions start returning"""
        # Search for all the raws in the detector_hierarchy with the parent_id column matching 
        # the self.parent_id of this object
#        self.curs.execute( "SELECT * FROM detector_hierarchy WHERE parent_id IS %s" %(self.id) )
        self.curs.execute( "SELECT * FROM detector_hierarchy WHERE parent_id=?", (self.id,) )
        childRows = self.curs.fetchall()
#        print "Found {0} children for parent with id {1}".format( len(childRows), self.id )

        # Create objects for the children
        childList = []        
        for child in childRows:
            childID = child["id"]
            newSubsystem = subsystem( self.curs, childID, self ) 
            childList.append(newSubsystem)
        return childList



    
# End of "subsystem" class definition
    


