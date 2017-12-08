'''
Created on August 5, 2014

This file contains a class to handle the alarm tree hierarchy  
in BEAST. This class is expected to be used for building MySQL 
database for the BEAST alarm system.  

@author: Hovanes Egiyan
'''
#import MySQLdb as mdb
#import os,sys
import copy

from beastComponent import beastComponent
from namedAlarmComponent import namedAlarmComponent


class beastComponentInDB(beastComponent):
    '''
    Class to handle a node in the alarm tree hierarchy in BEAST with an access to DB 
    '''
   
    @classmethod
    def copyComponent(cls, component, parent ):
        """
        Create a copy of a the component with the same name, but use 
        a different parent in general. Returns the instance of the 
        newly created component
        """
        newComp = beastComponentInDB( component.curs, component.component_id, parent )
        for child in component.children:
            newChild = beastComponentInDB.copyComponent(child, newComp)
            newComp.children.append(newChild)
        return newComp
   
   
   
    def __init__(self, inCursor=None, compID=None, parent=None, lvl=0 ):
        beastComponent.__init__(self, compID, parent)
        '''
        Constructor for the class. Creates the object, then to create objects for the children.
        That function will call the constructor for children, so the process will go recursively. 
        '''        
        self.curs       = inCursor  # cursor for the DB connector 
        self.level      = lvl       # Level # in the hierarchy
        
        # Find the fields for this component to assign the data members
        self.curs.execute( "SELECT * FROM ALARM_TREE WHERE COMPONENT_ID=%s", (compID,) )
        allComponents = self.curs.fetchall()
        
        # Raise an exception if there are too many rows from the previous SQL 
        # There has to be only one entry in the table for each unique id
        if( len( allComponents ) > 1 ):
            errMsg = "Too many detectors with COMPONENT_ID {0}, to be exact there are {1}".format(compID, len(allComponents) )
            print errMsg
            raise Exception( errMsg )
        if( len( allComponents ) < 1 ):
            errMsg = "No components with COMPONENT_ID {0}".format(compID, )
            print errMsg
            raise Exception( errMsg )
        
        # Find the first detector_hierarchy raw in the DB 
        component = allComponents[0]
#        print "Creating a component with {0} elements and COMPONENT_ID {1}".format(len(component), compID)
#        (self.id, self.parent_id, self.name, self.type,  self.chanid, dummy) = detector
        self.component_id       = component["COMPONENT_ID"]
        self.parent_cmpnt_id    = component["PARENT_CMPNT_ID"]
        self.name               = component["NAME"]
        self.config_time        = component["CONFIG_TIME"]
        
        # If cannot find the requested component in the DB then raise an exception 
        if( self.component_id == 0 ) :
            errMsg = "Bad alarm tree hierarchy <{0}>".format( compID )
            print errMsg
            raise Exception( errMsg )
 
        self.getAutomatedActions()
        self.getCommands()
        self.getDisplays()
        self.getGuidances()
        self.getPVattributes() 
#        self.convertNoneToNULL()
        # Keep going to find the children
        self.children   = self.findChildren()
#        print "Finished creating component ", self.getFullPath("/")

    
    def getArea(self):
        """
        Find the alarm area above this subsystem in the tree.
        """
        if( self.level == 0 ):
            return self
        else:
            return self.parentSys.getArea()
        
    
    def getDetector(self):
        """
        Find the detector above this subsystem in the tree.
        """
        if( self.level == 1 ):
            return self
        else:
            if( self.parentSys == None ):
                return None
            return self.parentSys.getDetector()

    def getSystem(self):
        """
        Find the alarm area above this subsystem in the tree.
        """
        if( self.level == 2 ):
            return self
        else:
            if( self.parentSys == None ):
                return None
            return self.parentSys.getSystem()
  
        
#     def getAlarmPVName(self):
#         """
#         Get the PV name for the alarm handler. 
#         """
#         pvName = self.name
#         if( namedAlarmComponent.pvPrefix != "" ):
#             pvName = namedAlarmComponent.pvPrefix + ":" + pvName 
#         return pvName
        
    def getAutomatedActions(self):
        self.automatedAction = []
        sql  = "SELECT TITLE, AUTO_ACTION_ORDER, DETAIL, DELAY FROM AUTOMATED_ACTION WHERE COMPONENT_ID = %s"
        self.curs.execute( sql, (self.component_id,) )
        allActions = self.curs.fetchall()
        for action in allActions:
            self.automatedAction.append( copy.deepcopy(action))
        return
       
    def getCommands(self):
        self.command = []
        sql  = "SELECT TITLE, COMMAND_ORDER, DETAIL FROM COMMAND WHERE COMMAND.COMPONENT_ID = %s"
        self.curs.execute( sql, (self.component_id,) )
        allCommands = self.curs.fetchall()
        for comd in allCommands:
            self.command.append( copy.deepcopy(comd) )
        return

    def getDisplays(self):
        self.display = []
        sql  = "SELECT TITLE, DISPLAY_ORDER, DETAIL FROM DISPLAY WHERE COMPONENT_ID = %s"
        self.curs.execute( sql, (self.component_id,) )
        allDisplays = self.curs.fetchall()
        for disp in allDisplays:
            self.display.append( copy.deepcopy(disp) )
        return
      
    def getGuidances(self):
        self.guidance = []
        sql  = "SELECT TITLE, GUIDANCE_ORDER, DETAIL FROM GUIDANCE WHERE COMPONENT_ID = %s"
        self.curs.execute( sql, (self.component_id,) )
        allGuidances = self.curs.fetchall()
        for guid in allGuidances:
            self.guidance.append( copy.deepcopy(guid) )
        return
        
        
    def getPVattributes(self):
        '''
        Get the PV attributes from the MySQL database of BEAST.
        Only try to find one single entry in the PV table that matches self.component_id
        '''
        self.pv = {}
        sql  = "SELECT DESCR, ENABLED_IND, ANNUNCIATE_IND, LATCH_IND, DELAY, FILTER, DELAY_COUNT, ACT_GLOBAL_ALARM_IND FROM PV WHERE COMPONENT_ID = %s"
        self.curs.execute( sql, (self.component_id,) )
        firstPV = self.curs.fetchone()
        if( firstPV != None and len( firstPV ) > 0 ):
            self.pv = copy.deepcopy(firstPV)
        return
            
#     def convertNoneToNULL(self):
#         '''
#         Convert all None-s to NULL-s in the attributes that came from DB. 
#         '''
#         for attrRows in [self.automatedAction, self.command, self.display, self.guidance] :
#             for attrDict in attrRows:
#                 for dictKey in attrDict.keys():
#                     if( attrDict[dictKey] == None ):
#                         attrDict[dictKey] = 'NULL'
#         for attribName in  self.pv.keys():
#             if( self.pv[attribName] == None ):
#                 self.pv[attribName] = 'NULL'
#         return
                               
    def findChildren(self):
        """Finds children of this component. Note that this function will create other 
        objects of this class which will in turn call this function. The recursive process 
        continues until we reach an object with no children found and the functions start returning"""
        # Search for all the raws in the component_hierarchy with the parent_id column matching 
        # the self.parent_id of this object
        self.curs.execute( "SELECT * FROM ALARM_TREE WHERE PARENT_CMPNT_ID=%s", (self.component_id,) )
        childRows = self.curs.fetchall()
#        print "Found {0} children for parent with COMPONENT_ID {1}".format( len(childRows), self.component_id )

        # Create objects for the children
        childList = []        
        for child in childRows:
            childID = child["COMPONENT_ID"]
            newSubsystem = beastComponentInDB( self.curs, childID, self, self.level+1 ) 
            childList.append(newSubsystem)
        return childList

        
    def makeAlarmEntries(self, sqlFile, parBeastID = None ):
        """ Recursively make entries into the BEAST SQL file """
        entryName = self.name
        # If the object does not have children, than turn this into a PV by making a PV entry in the SQL file
        if( len(self.children) == 0 ):
            entryName = self.getAlarmPVName()
        commentLine = "Entry for " + self.getFullPath() + " PV " + self.getAlarmPVName()
        sqlFile.makeCommentLine( commentLine )
        beastID = sqlFile.makeAlarmEntry( parBeastID, entryName )
        sqlFile.makeAlarmGuidances( beastID, self.guidance )
        sqlFile.makeAlarmCommands( beastID, self.command )
        sqlFile.makeAlarmAutomatedActions( beastID, self.automatedAction )
        sqlFile.makeAlarmDisplays( beastID, self.display )
        
        if( len( self.children ) == 0 ):
            sqlFile.makeAlarmPVs( beastID, self.pv )
        # Loop through the children and make entries for them as well 
        for child in self.children:
            child.makeAlarmEntries( sqlFile, beastID )            
        return beastID

    
# End of "beastComponentInDB" class definition
    


