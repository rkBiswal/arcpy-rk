# Name: UnAbandonSelectedFeatures.py
#
# Description: This python script is designed to run as a script tool. Scripts that evaluates 
# the Abandon Point and Abandon Line layers and moves the selected features back to the in service 
# layer.  The scripts determines which layer to store the feature in based on the value in the 
# POINTTYPE and LINETYPE field.  The selected features can optionally be deleted by setting the 
# Delete Features parameter to true.  You can specify a Key/Value pair to translate the value 
# used in the Type fields to the feature layer names.
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

#The input Abandon Line layer
Water_Abandoned_Lines = arcpy.GetParameterAsText(0)
if Water_Abandoned_Lines == '#' or not Water_Abandoned_Lines:
    Water_Abandoned_Lines = "Water Distribution System\\Water Network\\Water Abandoned Assets\\Water Abandoned Lines" # provide a default value if unspecified

#The input Abandon Point layer
Water_Abandoned_Points = arcpy.GetParameterAsText(1)
if Water_Abandoned_Points == '#' or not Water_Abandoned_Points:
    Water_Abandoned_Points = "Water Distribution System\\Water Network\\Water Abandoned Assets\\Water Abandoned Points" # provide a default value if unspecified

#The parameter to delete the feature
Delete_Features = arcpy.GetParameterAsText(2)
if Delete_Features == '#' or not Delete_Features:
    Delete_Features = "false" # provide a default value if unspecified

#The Abandon Lines Layer field that stores the source layers name or code
FieldInAbandonLinesToSet = arcpy.GetParameterAsText(3)
if FieldInAbandonLinesToSet == '#' or not FieldInAbandonLinesToSet:
    FieldInAbandonLinesToSet = "LINETYPE" # provide a default value if unspecified

#The Abandon Point Layer field that stores the source layers name or code
FieldInAbandonPointsToSet = arcpy.GetParameterAsText(4)
if FieldInAbandonPointsToSet == '#' or not FieldInAbandonPointsToSet:
    FieldInAbandonPointsToSet = "POINTTYPE" # provide a default value if unspecified

#The translation value record set
Translation_Values = arcpy.GetParameterAsText(5)
if Translation_Values == '#' or not Translation_Values:
    Translation_Values = "in_memory\\{44AD2A58-D849-4106-B493-4041B3FBCDDA}" # provide a default value if unspecified

#Create an array of the abandon layers
layers = (Water_Abandoned_Points, Water_Abandoned_Lines)

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

#Lopp through the Abandon Layers
for AbLayer in layers:

    #Describing Layer to get layer details
    abDes = arcpy.Describe(AbLayer)
    
    AbShapeFieldName = str(abDes.shapeFieldName)
    AbOIDFieldName = str(abDes.OIDFieldName)
    AbNameString = str(abDes.nameString)
    AbFeatureType = str(abDes.featureType)
    AbShapeType = str(abDes.shapeType)
    AbLenFld = str(abDes.lengthFieldName)
    AbfidSet = str(abDes.fidSet)
    
    #Determine Abandon Shape Type and use the appropriate fields
    if AbShapeType == "Point":
        abField = FieldInAbandonPointsToSet
    else:
        abField = FieldInAbandonLinesToSet
        
    #Cleanup  
    del abDes
    
    #Create Field list to ignore to check to copy over
    ignoreFields = []
    ignoreFields.append(str(AbShapeFieldName))
    ignoreFields.append(str(AbOIDFieldName))
    ignoreFields.append(str(AbLenFld))

    fields = arcpy.ListFields(AbLayer)
    fieldList = []
    
    #Create list of fields to check to copy over
    for field in fields:
        if field.name not in ignoreFields:
            fieldList.append(field.name)
    
    #Get access to the current MXD to look for target layers 
    mxd = arcpy.mapping.MapDocument("CURRENT")
    
    #Check to see if the layer has a selection set
    if AbfidSet == "":
        #No Selected Features
        arcpy.AddMessage(msgNoSelect + "%s" % AbLayer)
    else:
        #Layer has selected features    
        fids = AbfidSet.split(';')
        
        #Get number of selected features
        numSelect = len(fids)
          
        #Add feedback to the GP window
        arcpy.AddMessage(AbNameString + " is a " + str(AbShapeType) + " with " + str(numSelect) + " selected")
        
        #Determine which cursor to use depending the the features will be deleted
        if Delete_Features == "true":
            abCurs = arcpy.UpdateCursor(AbLayer, "", "", "", abField + " A")
        else:
            abCurs = arcpy.SearchCursor(AbLayer, "", "", "", abField + " A")
        
        #Verify the cursor is valid
        if abCurs == None:
            arcpy.AddMessage("Error getting cursor to the selected features")
        else:  
            #Initialize variables 
            row = None
            targetCur = None
            lastLay = ""
            translatedVal = ""
            targetShapeFieldName = ""
            targetDesc = ""
            targetShapeType = ""
            tragetFldInfo = ""
            #Loop through all rows
            for row in abCurs:
                
                #Build list of information to store feature, do it once per layer 
                if str(row.getValue(abField)) != lastLay:
                    
                    targetCur = None
                    #Get the layer name or code
                    lastLay = row.getValue(abField)

                    #Translate code to layer name if valid
                    if (str(lastLay) in ConversionForNames):
                        translatedVal = ConversionForNames[lastLay]
                      
                    else:
                        translatedVal = lastLay
                    
                    #Get list of matching layers
                    possibleLayers = arcpy.mapping.ListLayers(mxd, translatedVal)
                    
                    if len(possibleLayers) > 0:
                        
                        #Layer was found, add a message and describe it to get required information
                        arcpy.AddMessage(possibleLayers[0].name + " was found")
                        
                        targetDesc = ""
                        targetFldInfo = None
                        targetCur = arcpy.InsertCursor(possibleLayers[0])
                        targetDesc = arcpy.Describe(possibleLayers[0])
                        targetShapeType = str(targetDesc.shapeType)
                        targetFldInfo = targetDesc.FieldInfo
                        targetShapeFieldName = str(targetDesc.shapeFieldName)
                        
                        #Cleanup
                        del targetDesc  
                    else:
                        #No Layer found, continue to next record
                        row = None
                        targetCur = None
                        arcpy.AddMessage(translatedVal + " was not found")
                        continue
                
                #Proceed if the shape type matches and the insert cursor is valid
                if targetCur != None and targetShapeType == AbShapeType:
                    
                    #Create a new target feature    
                    newRow = targetCur.newRow()
                    
                    #Proceed if the row was created successfully
                    if newRow != None:
                        
                        #get and set the features shape
                        newRow.setValue(targetShapeFieldName, row.getValue(AbShapeFieldName))
                        
                        #Loop through the fields and copy matching values
                        for fieldName in fieldList:
                            if targetFldInfo.findFieldByName(fieldName) >= 0:                    
                                newRow.setValue(fieldName, row.getValue(fieldName))
                        
                        #Insert the row
                        targetCur.insertRow(newRow)
                        
                        #Delete the source row if user specified to do so
                        if Delete_Features:
                            abCurs.deleteRow(row)
                        arcpy.AddMessage("Feature Added to " + translatedVal)
                    else:
                        arcpy.AddMessage("Row was not created")
                else:
                    arcpy.AddMessage("Layer or shape is not valid")
            
            #Cleanup
            del row
            del targetCur
            del lastLay
            del translatedVal
            del targetShapeFieldName
          
            del targetShapeType
            del tragetFldInfo        
        
        #Cleanup
        del fids
        del numSelect 

#Cleanup        
del FieldInAbandonPointsToSet
del FieldInAbandonLinesToSet
del ConversionForNames
del msgSuccess
del msgWrongShape
del msgNoSelect
del msgFail
del msgCalculating
del Water_Abandoned_Lines
del Water_Abandoned_Points
del Delete_Features
del AbShapeFieldName
del AbOIDFieldName
del AbNameString
del AbFeatureType
del AbShapeType
del AbLenFld
del AbfidSet
del ignoreFields
del fields
del fieldList
del mxd
