'''
Created on Aug 13, 2014

@author: Hovanes Egiyan
'''

#from beastFile import beastFile

class namedAlarmComponent(object):
    '''
    class to handle hierarchy structure and EPICS alarm entry making
    for the nodes and PVs
    '''
    pvPrefix = ""
    
    @classmethod
    def copyOfNamedAlarmComponent(cls, component, parent ):
        """
        Create a copy of a the component with the same name, but use 
        a different parent in general. Returns the instance of the 
        newly created component
        """
        newComp = namedAlarmComponent( component.name, parent )
        for child in component.children:
            newChild = namedAlarmComponent.copyOfNamedAlarmComponent(child, newComp)
            newComp.children.append(newChild)
        return newComp
    

    def __init__(self, compName, parent=None ):
        '''
        Constructor
        '''
        self.name = compName
        self.children = []  
        self.parentSys = parent
        return
    
    def __del__(self):
        """
        Delete all children of this object
        """
        for child in self.children:
            self.children.remove(child)
            del child            
        return
        
    def __str__(self):
        retString = "\nComponent with name {0}".format( self.name )
        if( len(self.children)>0 ) : 
            retString += "\nChildren are "       
        for child in self.children:
            retString += str(child)
        retString += "\nFull path is " + self.getFullPath("/") 
        return retString
        
    def __repr__(self):
        retString = "\nComponent with name {0}".format( self.name )
        if( len(self.children)>0 ) : 
            retString += "\nChildren are "
        for child in self.children:
            retString += str(child)
        retString += "\nFull path is " + self.getFullPath("/") 
        return retString
        
    
    def getChildrenNames(self):
        """
        return the sorted list of the children's name
        """
        nameList = []
        for child in self.children:
            nameList.append( child.name )
        return nameList

    def getChild(self, childName ):
        for child in self.children:
            if( child.name == childName ):
                return child
        return None


    
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
        
        if( self.name != component.name ):
            newCompDict[component.getFullPath()] = component
            return newCompDict

        if( len(component.children) > 0 ):
            for othersChild in component.children:
                if( othersChild.name not in self.getChildrenNames()  ) :
                    newCompDict[othersChild.getFullName()] = othersChild
                else :
                    newCompsInChild = self.getChild( othersChild.name ).findNewComponents( othersChild )
                    if( len(newCompsInChild) > 0 ) :
                        newCompDict.update( newCompsInChild )
        return newCompDict
    
    
    def findMissingComponents(self, component):
        missingCompDict = {}
        if( component == None ):
            missingCompDict[self.getFullPath()] = self
            return missingCompDict

        if( self.name != component.name ):
            missingCompDict[self.getFullPath()] = self
            return missingCompDict

        if( len(self.children) > 0 ) :
            for ownChild in self.children:
                if( ownChild.name not in component.getChildrenNames() ) :
                    missingCompDict[ownChild.getFullName()] = ownChild
                else :
                    missingCompDict.update( self.getChild( ownChild.name ).findMissingComponents( component.getChild( ownChild.name ) ) )
                    
        return missingCompDict
    
    
    def __eq__(self, component ):
        if( len( self.findMissingComponents(component) ) != 0 or len( self.findNewComponents(component) ) != 0  ):
            return False
        return True
    
    def __ne__(self, component ):
        if( len( self.findMissingComponents(component) ) == 0 and len( self.findNewComponents(component) ) == 0  ):
            return False
        return True

    

    def getSubComponent( self, relativePath ):
        """
        Return the component specified by the path string in format "A/B/C/D/".
        This will return the component whose name is D on the forth layer of hierarchy 
        with parenting sequence defined by the string above.
        """
        if( relativePath == "" ):
            return self
        if( len(self.children) == 0 ):
            return None      
#        if( relativePath.find("/") == -1 ):
        
        listOfNames = relativePath.split( "/" )        
        childName = listOfNames[0] 
#         if( childName == '' ):
#             return None             
        child = self.getChild( childName )
        if( child == None ) :
            return None
        else :
#             if( len(listOfNames) == 1 ) :
#                 return self
#             else:
            string2remove = childName 
            if( len(listOfNames) > 1 ):
                string2remove += "/"
            return child.getSubComponent( relativePath.replace( string2remove, "" ) )
            
#         print "Name is ", self.name , " full name is ", self.getFullName()
#         reducedPath = relativePath
#         print "Original path is ", reducedPath
#         string2remove = self.name+"/"
#         print "String to remove is ", string2remove
#         reducedPath = relativePath.replace( string2remove, "" )
#         print "Reduced path is ", reducedPath
#         
#         # If we got to the bottom then return this component
#         if( reducedPath == "" ) :
#             return self
#         # else go down to the next level
#         else:
#             for child in self.children :
#                 subComp = child.getSubComponent( reducedPath )
#                 if( subComp != None ) :
#                     return subComp
# #            print "Did not find subcomponent ", path, " in ", self.getFullPath()
#             return None


    def insertComponent(self, comp):
        '''
        Insert a new component into this component
        '''
        print "In  insertComponent for ", self.getFullPath(), " with ", comp.getFullPath()
        if( comp.name in self.getChildrenNames() ):
            errMsg = "Subcomponent named {0} already exists in {1}".format(comp.name, self.getFullPath() )
            print errMsg
            raise Exception( errMsg )
#        newComponent = namedAlarmComponent.copyOfNamedAlarmComponent(comp, self)
        newComponent = comp.__class__.copyComponent(comp, self)
        self.children.append( newComponent )
        return
    
    def removeComponent(self, comp):
        '''
        Remove a particular component from self, if exists. 
        The component to be removed is deleted.
        '''
        print "In removeComponent for ", self.getFullPath(), " with ", comp.getFullPath()
        if(  comp.name not in self.getChildrenNames() ):
            errMsg = "Subcomponent named {0} does not exist in {1}".format(comp.name, self.getFullPath() )
            print errMsg
            raise Exception( errMsg )        
        self.children.remove(comp)
        del comp
        return
    
   
    def getRootSystem(self):
        """Find the top level subsystem (AREA) above this subsystem in the tree"""
        if( self.parentSys == None ):
            return self
        else:
            return self.parentSys.getRootSystem()

   
    def getFullName(self, separator=":"):
        """Return the full path (or the PV name base) for this subsystem in the tree.
        The full path is the fully classified name of the detector element, the top level 
        element starting from the left. The detector levels are separated by a string give 
        by the separator parameter"""
        if( self.parentSys == None ):
            return self.name
        else:
            return self.parentSys.getFullName(separator) + separator + self.name
    
    def getFullPath(self, separator = "/"):
        return separator + self.getFullName( separator )
    

    def getAlarmGuidance(self):
        """ Get the guidance for this particular subsystem"""
        areaName = self.getRootSystem().name
        print "areaName is " , areaName
        guidance = "Page expert for component " + areaName 
        return guidance
    

    def getAlarmDescription(self):
        """ Get the description for the EPICS variable """
        description = "Voltage alarm for " +  self.getFullName( " : " )
        return description


    def getAlarmPVName(self):
        """Get the PV name for the alarm handler. PV name starts with a prefix, 
        followed by the full path using semicolon separator, and ending with 
        a suffix 'alarm' to identify EPICS record name"""
        pvName = self.getFullName(":") #+ ":alarm"
        if( namedAlarmComponent.pvPrefix != "" ):
            pvName = namedAlarmComponent.pvPrefix + ":" + pvName 
        return pvName
    
    
#     def makeAlarmEntries(self, sqlFile, parBeastID ):
#         """ Recursively make entries into the BEAST SQL file """
#         entryName = self.name
#         # If the object does not have children, than turn this into a PV by making a PV entry in the SQL file
#         if( len(self.children) == 0 ):
#             entryName = self.getAlarmPVName()
#         beastID = sqlFile.makeAlarmEntry( parBeastID, entryName )
#         self.makeAlarmGuidance( sqlFile, beastID )
#         self.makeAlarmPV(sqlFile, beastID)
#         # Loop through the children and make entries for them as well 
#         for child in self.children:
#             child.makeAlarmEntries( sqlFile, beastID )            
#         return beastID        

    def makeAlarmPV(self, sqlFile, beastID):
        """ Make PV entry for subsystems on the bottom of the detector tree into the SQL file"""
        if( len(self.children) == 0 ):
            sqlFile.makeAlarmPV( beastID, self.getAlarmDescription() )
        return 
    

    def makeAlarmGuidance(self, sqlFile, beastID):
        """ Put the guidance information into the SQL file"""
        sqlFile.makeAlarmGuidance( beastID, self.getAlarmGuidance() )
        return 
       