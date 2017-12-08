'''
Created on August 5, 2014

This file contains a class to handle the alarm tree hierarchy  
in BEAST. This class is expected to be used for building MySQL 
database for the BEAST alarm system.  

@author: Hovanes Egiyan
'''
#import os,sys

#from beastFile import beastFile

from namedAlarmComponent import namedAlarmComponent


class beastComponent(namedAlarmComponent):
    '''
    Class to handle a node in the alarm tree hierarchy in BEAST 
    '''
   
    def __init__(self, compID=None, parent=None):
        '''
        Constructor for the class. Creates the object, then to create objects for the children.
        That function will call the constructor for children, so the process will go recursively. 
        '''
        namedAlarmComponent.__init__(self, None, parent)
        self.component_id           = compID    # id in the alarm hierarchy DB
        self.parent_cmpnt_id        = None      # paprent_id in the alarm hierarchy tree
        self.config_time            = None      # type in the alarm hierarchy tree
        
        if( self.parentSys != None ) :
            self.parent_cmpnt_id = parent.component_id
            
        self.guidance       = []
        self.command        = []
        self.automatedAction= []
        self.display        = []
        self.pv             = None
        
        '''Define the list of main attributes using which the two component would be considered equal or not'''
        self.mainAttributes = {"name"               :   self.name, 
                               "guidance"           :   self.guidance, 
                               "command"            :   self.command,
                               "automatedAction"    :   self.automatedAction, 
                               "display"            :   self.display, 
                               "pv"                 :   self.pv }
        return
        
            
    
    def __str__(self):
        retString = "\nSubsystem with COMPONENT_ID {0},  PARENT_CMPNT_ID {1}, NAME {2}, CONFIG_TIME {3}".format(self.component_id, self.parent_cmpnt_id, self.name, self.config_time )
        if( len(self.children)>0 ) : 
            retString += "\nChildren are "       
        for child in self.children:
            retString += str(child)
        retString += "\nFull path is " + self.getFullPath("/") 
        return retString
        
    def __repr__(self):
        retString = "\nSubsystem with COMPONENT_ID {0},  PARENT_CMPNT_ID {1}, NAME {2}, CONFIG_TIME {3}".format(self.component_id, self.parent_cmpnt_id, self.name, self.config_time )
        if( len(self.children)>0 ) : 
            retString += "\nChildren are "
        for child in self.children:
            retString += str(child)
        retString += "\nFull path is " + self.getFullPath("/") 
        return retString
        

    def getAlarmPVName(self):
        """
        Get the PV name for the alarm handler. 
        """
        pvName = self.name
        if( namedAlarmComponent.pvPrefix != "" ):
            pvName = namedAlarmComponent.pvPrefix + ":" + pvName 
        return pvName
                       
    def getFullIdentity(self):
        '''returns a list of the main attributes including the attributes of the parent'''
        if( self.parentSys == None ):
            return [self.mainAttributes]
        else:
            return self.parentSys.getFullIdentity().append( self.mainAttributes )
    
    
        
    def getChildByAttributes(self, childMainAttributes ):
        '''
        Return the first child that has the specified attributes
        '''
        for child in self.children:
            if( child.mainAttributes == childMainAttributes ):
                return child
        return None

    def getChildrenMainAttributes(self):
        """
        return the sorted list of the children's main attributes
        """
        attributeList = []
        for child in self.children:
            attributeList.append( child.mainAttributes )
        return attributeList
        
    def findNewComponents(self, component):
        """
        Find new components in the 'component' and return a map 
        with all the new components that are not in self component. 
        The key is going to be the full path to the new components.
        Here we assume that the only parameter that define the identity 
        of the component is its name and that a component cannot have the two children 
        with the same name. The fact that the names are same does not mean 
        that the components are the same. 
        """
        newCompDict = {}
        if( component == None ):
            return newCompDict
        
        if( self.mainAttributes != component.mainAttributes ):
            newCompDict[component.getFullPath()] = component
            return newCompDict

        if( len(component.children) > 0 ):
            for othersChild in component.children:
                if( othersChild.mainAttributes not in self.getChildrenMainAttributes()  ) :
                    newCompDict[othersChild.getFullName()] = othersChild
                else :
                    newCompsInChild = self.getChildByAttributes( othersChild.mainAttributes ).findNewComponents( othersChild )
                    if( len(newCompsInChild) > 0 ) :
                        newCompDict.update( newCompsInChild )
        return newCompDict
        
    def findMissingComponents(self, component):
        missingCompDict = {}
        if( component == None ):
            missingCompDict[self.getFullPath()] = self
            return missingCompDict

        if( self.mainAttributes != component.mainAttributes ):
            missingCompDict[self.getFullPath()] = self
            return missingCompDict

        if( len(self.children) > 0 ) :
            for ownChild in self.children:
                if( ownChild.mainAttributes not in component.getChildrenMainAttributes() ) :
                    missingCompDict[ownChild.getFullName()] = ownChild
                else :
                    missCompsInChild = self.getChildByAttributes( ownChild.mainAttributes ).findMissingComponents( component.getChildByAttributes( ownChild.mainAttributes ) )
                    if( len(missCompsInChild) > 0 ) :
                        missingCompDict.update( missCompsInChild )
                    
        return missingCompDict
    
    def __eq__(self, component ):
        if( len( self.findMissingComponents(component) ) != 0 or len( self.findNewComponents(component) ) != 0  ):
            return False
        return True
    
    def __ne__(self, component ):
        if( len( self.findMissingComponents(component) ) == 0 and len( self.findNewComponents(component) ) == 0  ):
            return False
        return True

    
# End of "beastComponent" class definition
    


