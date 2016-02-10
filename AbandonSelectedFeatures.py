# Name: AbandonSelectedFeatures.py
#
# Description: This python script is designed to run as a script tool. It evaluates a series of input
# layers and moves the selected features to the target point and polyline layers.  The scripts determines 
# based on shape which target layer to move the features to.  The selected features can optionally be
# deleted by setting the Delete Features parameter to true.  You can specify a Key/Value pair to translate 
# the input feature layer names to a code or some other value to store in the POINTTYPE or LINETYPE field.
#
# Requirements: ArcEditor or ArcInfo License
# Author: Mike Miller - ArcGISTeamLocalGov

import arcpy


msgSuccess = "Successfully processed features : "
msgWrongShape = "Wrong Shape Type - Only Points and Lines : "
msgNoSelect = "No Selected Features : "

msgFail = "Failed to process features : "
msgCalculating = "Moving features : "

arcpy.AddMessage("Starting Abandon Selected Features Script")
arcpy.AddMessage("Processing Parameters")

#The input layers
Layers = arcpy.GetParameterAsText(0)
if Layers == '#' or not Layers:
    Layers = "'Water Distribution System\\Water Network\\Water Mains';'Water Distribution System\\Water Network\\Water Fittings'" # provide a default value if unspecified
Layers = str(Layers).replace("'", "")
Layers = str(Layers).split(';')

#The Abandon Lines Layer
Water_Abandoned_Lines = arcpy.GetParameterAsText(1)
if Water_Abandoned_Lines == '#' or not Water_Abandoned_Lines:
    Water_Abandoned_Lines = "Water Distribution System\\Water Network\\Water Abandoned Assets\\Water Abandoned Lines" # provide a default value if unspecified

#The Abandon Point Layer
Water_Abandoned_Points = arcpy.GetParameterAsText(2)
if Water_Abandoned_Points == '#' or not Water_Abandoned_Points:
    Water_Abandoned_Points = "Water Distribution System\\Water Network\\Water Abandoned Assets\\Water Abandoned Points" # provide a default value if unspecified

#The parameter to delete the feature
Delete_Features = arcpy.GetParameterAsText(3)
if Delete_Features == '#' or not Delete_Features:
    Delete_Features = "false" # provide a default value if unspecified

#The Abandon Lines Layer field to store the source layers name or code
FieldInAbandonLinesToSet = arcpy.GetParameterAsText(4)
if FieldInAbandonLinesToSet == '#' or not FieldInAbandonLinesToSet:
    FieldInAbandonLinesToSet = "LINETYPE" # provide a default value if unspecified

#The Abandon Point Layer field to store the source layers name or code
FieldInAbandonPointsToSet = arcpy.GetParameterAsText(5)
if FieldInAbandonPointsToSet == '#' or not FieldInAbandonPointsToSet:
    FieldInAbandonPointsToSet = "POINTTYPE" # provide a default value if unspecified

#The translation value record set
Translation_Values = arcpy.GetParameterAsText(6)

#Create Cursors to insert data into abandon layers
pointCurs = arcpy.InsertCursor(Water_Abandoned_Points) 
polyCurs = arcpy.InsertCursor(Water_Abandoned_Lines) 


#Describing the Abandon Line layer to get layer details
descAbLines = arcpy.Describe(Water_Abandoned_Lines)

AbLinesShapeFieldName = str(descAbLines.shapeFieldName)
AbLinesOIDFieldName = str(descAbLines.OIDFieldName)
AbLinesNameString = str(descAbLines.nameString)
AbLinesFeatureType = str(descAbLines.featureType)
AbLinesShapeType = str(descAbLines.shapeType)
AbLinesLenFld = str(descAbLines.lengthFieldName)

#Describing the Abandon Points layer to get layer details
descAbPoints = arcpy.Describe(Water_Abandoned_Points)

AbPointsShapeFieldName = str(descAbPoints.shapeFieldName)
AbPointsOIDFieldName = str(descAbPoints.OIDFieldName)
AbPointsNameString = str(descAbPoints.nameString)
AbPointsFeatureType = str(descAbPoints.featureType)
AbPointsShapeType = str(descAbPoints.shapeType)

#Delete the Describe objects for better memory management
del descAbLines
del descAbPoints

#Create list of fields to ignore searching for in the input point feature
ignoreFieldsPoints = []
ignoreFieldsPoints.append(str(AbPointsShapeFieldName))
ignoreFieldsPoints.append(str(AbPointsOIDFieldName))

#Create list of fields to ignore searching for in the input line feature
ignoreFieldsLines = []
ignoreFieldsLines.append(str(AbLinesShapeFieldName))
ignoreFieldsLines.append(str(AbLinesOIDFieldName))
ignoreFieldsLines.append(str(AbLinesLenFld))
         
#List the fields in the Abandon layer and add them to an array, these fields are used to look for a value  
#in the input point layer
fieldsPoints = arcpy.ListFields(Water_Abandoned_Points)
fieldListPoints = []
for field in fieldsPoints:
    if field.name not in ignoreFieldsPoints:
        fieldListPoints.append(field.name)

#List the fields in the Abandon layer and add them to an array, these fields are used to look for a value  
#in the input line layer
fieldsLines = arcpy.ListFields(Water_Abandoned_Lines)
fieldListLines = []
for field in fieldsLines:
    if field.name not in ignoreFieldsLines:
        fieldListLines.append(field.name)


#Get a cursor to the translation recordset 
rows = arcpy.SearchCursor(Translation_Values)

#Get the fields 
fieldList = arcpy.ListFields(Translation_Values)

#initialize the Translation Dictionary
ConversionForNames = {}

#Loop through each input row and add it to the conversion dict
for row in rows: 
    ConversionForNames[row.getValue(fieldList[1].name)] = row.getValue(fieldList[2].name)
    del row

#Cleanup
del fieldList
del rows

#Get the count on input layers
layCount = len(Layers)

#Set the progressor to the number of layers to loop through
arcpy.SetProgressor("step", "Moving Features", 0, layCount, 1) 
        
#Loop through all input layers
for lay in Layers:
    try:
        #Describing Layer to get layer details
        desc = arcpy.Describe(lay)
      
        shapefieldname = str(desc.ShapeFieldName)
        shapeType = str(desc.shapeType)
        nameString = str(desc.nameString)
        name = str(desc.name)
        featType = str(desc.featureType)
       
        fidSet = str(desc.fidSet)
        fldInfo = desc.FieldInfo
        names = nameString.split('\\')
        nameString = names[len(names) - 1]
        valueToStore = nameString
        
        #Cleanup
        del desc
        
        arcpy.AddMessage("Abandoning Selected Features in " + name)
        
        #Looking in translation dictionary from the name of the layer
        if (nameString in ConversionForNames):
            valueToStore = ConversionForNames[nameString]
            
        else:
            valueToStore = nameString
        
        #Check to see if the layer has a selection set                
        if fidSet == "":            
            #No Selected Features
            arcpy.AddMessage(msgNoSelect + "%s" % nameString)
        else:
            #Layer has selected features
            fids = fidSet.split(';')
            
            #Get number of selected features
            numSelect = len(fids)
            
            #Add feedback to the GP window
            arcpy.AddMessage(nameString + " is a " + str(shapeType) + " with " + str(numSelect) + " selected")

            #Check feature geometry type
            if str(shapeType) == "Polyline":
                #Determine which cursor to use depending the the features will be deleted
                if Delete_Features:
                    rows = arcpy.UpdateCursor(lay)
                else:
                    rows = arcpy.SearchCursor(lay)
                
                row = None
                #Loop through all rows
                for row in rows:
                    #Create a new row in the target layer
                    newRow = polyCurs.newRow()
                
                    #get and set the features shape
                    newRow.setValue(AbLinesShapeFieldName, row.getValue(shapefieldname))
                    
                    #Loop through the Target layers field list and look for values in source features
                    for fieldName in fieldListLines:
                        if fldInfo.findFieldByName(fieldName) >= 0:                    
                            newRow.setValue(fieldName, row.getValue(fieldName))
                    
                    #Store the layer name or code
                    newRow.setValue(FieldInAbandonLinesToSet, valueToStore)
                    
                    #insert and store the new row
                    polyCurs.insertRow(newRow)
                    
                    #Delete the source row if user specified to do so
                    if Delete_Features == "true":
                        rows.deleteRow(row)
                    
                    #delete the row to clean up memory
                    del newRow
                    
                    
                #add a message to show user layer was succesful     
                arcpy.AddMessage(msgSuccess + "%s" % nameString)        
                
                #Cleanup
                del rows
                del row
                
            elif str(shapeType) == "Point":
                #Determine which cursor to use depending the the features will be deleted
                if Delete_Features:
                    rows = arcpy.UpdateCursor(lay)
                else:
                    rows = arcpy.SearchCursor(lay)
                row = None
                #Loop through all rows
                for row in rows:
                    #Create a new row in the target layer
                    newRow = pointCurs.newRow() 
                    #get and set the features shape
                    newRow.setValue(AbPointsShapeFieldName, row.getValue(shapefieldname))
                    
                    #Loop through the Target layers field list and look for values in source features
                    for fieldName in fieldListPoints:
                        if fldInfo.findFieldByName(fieldName) >= 0:                    
                            newRow.setValue(fieldName, row.getValue(fieldName))
                            
                    #Store the layer name or code
                    newRow.setValue(FieldInAbandonPointsToSet, valueToStore)
                    
                    #insert and store the new row
                    pointCurs.insertRow(newRow)
                    
                    #Delete the source row if user specified to do so
                    if Delete_Features == "true":
                        rows.deleteRow(row)
                        
                    #delete the row to clean up memory
                    del newRow
                    
                #add a message to show user layer was succesful    
                arcpy.AddMessage(msgSuccess + "%s" % nameString)
                
                #Cleanup        
                del rows
                del row
                
            else:
                #Message if wrong input features where included
                arcpy.AddMessage(msgWrongShape + "%s" % nameString)                                    
        
        
        
        #Cleanup
        del shapefieldname
        del shapeType
        del nameString
        del featType
        del fidSet
        del fldInfo
        del names
       
        del valueToStore
        
    except Exception, e:
        import traceback
        map(arcpy.AddError, traceback.format_exc().split("\n"))
        arcpy.AddError(str(e))
    
    arcpy.SetProgressorPosition()
   
arcpy.ResetProgressor()

arcpy.AddMessage("Script Complete")

#Cleanup
del Water_Abandoned_Points, Water_Abandoned_Lines,
del msgSuccess, msgWrongShape, msgNoSelect, msgFail, msgCalculating
del Layers

del ConversionForNames
del AbLinesLenFld
del AbLinesOIDFieldName
del AbPointsOIDFieldName
del AbPointsShapeFieldName
del AbPointsNameString
del AbPointsFeatureType
del AbPointsShapeType
del AbLinesShapeFieldName
del AbLinesNameString
del AbLinesFeatureType
del AbLinesShapeType
