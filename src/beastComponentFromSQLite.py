'''
Created on August 5, 2014

This file contains a class to handle the alarm tree hierarchy  
in BEAST. This class is expected to be created from the GlueX 
detector subsystem tree class. It inherits from  beastComponent 
base class.

@author: Hovanes Egiyan
'''
import lxml.etree

from beastComponent import beastComponent




class beastComponentFromSQLite(beastComponent):
    '''
    Class to handle a node in the alarm tree hierarchy in BEAST with an access to DB 
    '''
    
    displayDict        = {}     # Detector specific map for OPI file names
    displayDictSTD     = {}     # Detector-independent map for OPI file names

    componentID = 0;            # component_id for this class
    
    @classmethod
    def copyComponent(cls, component, parent ):
        """
        Create a copy of a the component with the same name, but use 
        a different parent in general. Returns the instance of the 
        newly created component
        """
        newComp = beastComponentFromSQLite( component.subsys, component.component_id, parent )
        for child in component.children:
            newChild = beastComponentFromSQLite.copyComponent(child, newComp)
            newComp.children.append(newChild)
        return newComp   
    
        
    @classmethod
    def getNextComponentID(cls):
        """Calculate the next component_id for this tree"""
        beastComponentFromSQLite.componentID += 1
        return beastComponentFromSQLite.componentID
       
    @classmethod
    def initDisplayDictionaries(cls):
        """ Initialize the display name maps """
        # Common map for most detectors
        beastComponentFromSQLite.displayDictSTD = {
                          "hv"     :   "/Hall-D/Default/ALARMS/Voltages/ShowHVChannel.opi",
                          "lv"     :   "/Hall-D/Default/ALARMS/Voltages/ShowLVChannel.opi",
                          "bias"   :   "/Hall-D/Default/ALARMS/Voltages/ShowBiasChannel.opi"
        }
        # FCAL has a different HV OPI file
        beastComponentFromSQLite.displayDict["FCAL"]     = {
                                        "hv"    : "/Hall-D/Default/ALARMS/Voltages/ShowBaseChannel.opi", 
                                        "lv"     :   "/Hall-D/Default/ALARMS/Voltages/ShowLVChannel.opi",
                                        "bias"   :   "/Hall-D/Default/ALARMS/Voltages/ShowBiasChannel.opi"  
        }
        return 0

   
    def __init__(self, inSubsystem, compID=None, parent=None ):
        beastComponent.__init__(self, beastComponentFromSQLite.getNextComponentID(), parent)
        '''
        Constructor for the class. Creates the object, then to create objects for the children.
        That function will call the constructor for children, so the process will go recursively. 
        '''        
        self.subsys             = inSubsystem  
                        
#        print "Creating a component with {0} elements and COMPONENT_ID {1}".format( len(self.subsys.children), self.component_id)
        self.name               = inSubsystem.name
        self.config_time        = inSubsystem.mtime
        self.type               = inSubsystem.type
        
        
        # If cannot find the requested component in the DB then raise an exception 
        if( self.component_id == 0 ) :
            errMsg = "Bad alarm tree hierarchy <{0}>".format( compID )
            print errMsg
            raise Exception( errMsg )
 
        # In case it is the last leaf on the branch the name should be the PV name (with alarm) 
        # to match what comes out from the BEAST MYSQL database
        if( len( self.subsys.children ) == 0  ) :
            self.name = inSubsystem.getAlarmPVName()
 
        self.getGuidances()
        self.getDisplays()
        
        if( self.subsys.chanid != None ):
            self.getPVattributes()
 
        # Keep going to find the children
        for subSysChild in self.subsys.children :
            self.children.append( beastComponentFromSQLite( subSysChild, None, self ) )
 
#        print "Finished creating component ", self.getFullPath("/"), " pv name is ", self.getAlarmPVName()
        return


    def getDetector(self):
        """
        Find the detector above this subsystem in the tree.
        Uses the fact that the type for the detector node should have "Detector" 
        in the corresponding SQLite database entry. 
        """
        if( self.type ==  'Detector' ):
            return self
            if( self.parentSys == None ):
                return None
        else:
            return self.parentSys.getDetector()
        
    def getSystem(self):
        """
        Find the detector above this subsystem in the tree.
        Uses the fact that the type for the detector node should have "Voltage type" 
        in the corresponding SQLite database entry. 
        """
        if( self.type ==  'Voltage type' ):
            return self
        else:
            if( self.parentSys == None ):
                return None
            return self.parentSys.getSystem()
   
    def getGuidances(self):
        '''
        Set the guidance dictionary
        '''
        detector = self.getDetector()
        if( detector == None ) :
            return 
        suggestedAction = "Try to reset the voltage channel for " + \
            self.name.replace( ":alarm", "" ).replace(":", "->") + " . "
        suggestedAction += "You can use the associated screen to access voltage parameters for this channel. "
        suggestedAction += "If the problem still persists contact expert for " + detector.name + " detector."
        guideLine = {"TITLE"            :   "Guidance", 
                     "GUIDANCE_ORDER"   :   "0", 
                     "DETAIL"           :   suggestedAction}
        self.guidance.append( guideLine )
        return


    def getDisplays(self):
        """
        Set the related display dictionary
        """
        relatedDisplayName = ""
        
        detector = self.getDetector()
        if( detector == None ) :
            return

        system = self.getSystem()
        if( system == None ):
            return
        
        if( detector.name in beastComponentFromSQLite.displayDict.keys() ):
            relatedDisplayName = beastComponentFromSQLite.displayDict[detector.name][system.name]
        else:
            relatedDisplayName = beastComponentFromSQLite.displayDictSTD[system.name]
        displayWithMacro = relatedDisplayName + "   " +  '"pvName=' + self.name + '"'
        relatedDisplay = {"TITLE"           :   "Show voltage channel", 
                          "DISPLAY_ORDER"   :   "0", 
                          "DETAIL"          :   displayWithMacro }
        self.display.append(relatedDisplay)
        return

    def getPVattributes(self):
        '''
        Get the PV attributes for voltage channels from SQLite
        '''
        pvDescription  = "Voltage alarm for " + self.name.replace( ":alarm", "" ).replace(":", " : ")
        self.pv = {"DESCR"                  :   pvDescription, 
                   "ENABLED_IND"            :   1, 
                   "ANNUNCIATE_IND"         :   'true', 
                   "LATCH_IND"              :   'true', 
                   "DELAY"                  :   2, 
                   "DELAY_COUNT"            :   0, 
                   "FILTER"                 :   "",
                   "ACT_GLOBAL_ALARM_IND"   :   0}
        return


        
    def makeAlarmEntries(self, sqlFile, parBeastID ):
        """ Recursively make entries into the BEAST SQL file """
        
        entryName = self.name
        # If the object does not have children, than turn this into a PV by making a PV entry in the SQL file
        if( len(self.children) == 0 ):
            entryName = self.getAlarmPVName()
        commentLine = "Entry for " + self.getFullPath() + " PV " + self.getAlarmPVName()
        sqlFile.makeCommentLine( commentLine )
        beastID = sqlFile.makeAlarmEntry( parBeastID, entryName )
       
        if( len( self.children ) == 0 ):
            sqlFile.makeAlarmPVs( beastID, self.pv )
            sqlFile.makeAlarmGuidances( beastID, self.guidance )
            sqlFile.makeAlarmCommands( beastID, self.command )
            sqlFile.makeAlarmAutomatedActions( beastID, self.automatedAction )
            sqlFile.makeAlarmDisplays( beastID, self.display )
             
        # Loop through the children and make entries for them as well 
        for child in self.children:
            child.makeAlarmEntries( sqlFile, beastID )            
        return beastID

    
    def makeXMLElement( self, xmlRoot = None ):
        '''
        Create an XML element from the current component using its 
        attributes and recursively adds the branches for its children 
        to the element. Return an XML element corresponding to the 
        current BEST component. 
        '''        
        
        ''' 
        A dictionary for translating the names of the columns in the MySQL PV table and the 
        tag name in the corresponding "pv" tag in the XML file created from BEAST MySQL DB. 
        '''             
        xmlTagName = {"DESCR"               :   "description", 
                      "ENABLED_IND"         :   "enabled", 
                      "ANNUNCIATE_IND"      :   "annunciating", 
                      "LATCH_IND"           :   "latching", 
                      "DELAY"               :   "delay", 
                      "DELAY_COUNT"         :   "count", 
                      "FILTER"              :   "filter"
        }
        
        if( xmlRoot == None ):
            configElement = lxml.etree.Element( "config", name = "HallD" )
            xmlRoot = configElement

        elementName = "component"
        if( self.pv != None ) :
            elementName = "pv"
        newElement = lxml.etree.SubElement( xmlRoot, elementName, name = self.name )
        
        if( self.pv == None ):
            ''' Make elements for children if this tag is not for a PV'''
            for child in self.children :
                childElememt = child.makeXMLElement( newElement )
                newElement.append( childElememt )
        else:
            ''' if this is a PV then make the tags for PV attributes '''
            ''' Make the Guidance tags '''
            for guide in self.guidance :
                guideElement = lxml.etree.SubElement( newElement, "guidance" )
                titleElement = lxml.etree.SubElement( guideElement, "title" )
                titleElement.text = guide["TITLE"]
                detailElement = lxml.etree.SubElement( guideElement, "details" )
                detailElement.text = guide["DETAIL"]
            ''' Make the related display tags '''
            for disp in self.display:
                dispElement = lxml.etree.SubElement( newElement, "display" )
                titleElement = lxml.etree.SubElement( dispElement, "title" )
                titleElement.text = disp["TITLE"]
                detailElement = lxml.etree.SubElement( dispElement, "details" )
                detailElement.text = disp["DETAIL"]
            
            
            ''' Make command tags '''
            for cmd in self.command:
                cmdElement = lxml.etree.SubElement( newElement, "command" )
                titleElement = lxml.etree.SubElement( cmdElement, "title" )
                titleElement.text = cmd["TITLE"]
                detailElement = lxml.etree.SubElement( cmdElement, "details" )
                detailElement.text = cmd["DETAIL"]
            ''' Make automated action tags'''
            for act in self.automatedAction:
                actElement = lxml.etree.SubElement( newElement, "automated_action" )
                titleElement = lxml.etree.SubElement( actElement, "title" )
                titleElement.text = act["TITLE"]
                detailElement = lxml.etree.SubElement( actElement, "details" )
                detailElement.text = act["DETAIL"]
                delayElement = lxml.etree.SubElement( actElement, "delay" )
                delayElement.text = act["DELAY"]
            
            
            for pvAttrib in self.pv.keys():
                if pvAttrib in xmlTagName :
#                    print "PV Attribute is ", pvAttrib,  "TagName is ", xmlTagName[pvAttrib]
                    attribElement = lxml.etree.SubElement( newElement, xmlTagName[pvAttrib] )
                    attribElement.text = str( self.pv[pvAttrib] )
            
            
                
        return newElement
           
            
        
# End of "beastComponentFromSQLite" class definition


beastComponentFromSQLite.initDisplayDictionaries() 

