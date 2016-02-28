## Need to make a new field that starts at 10,000 and increments by 1 until it is filled

import arcpy

## Option -- 1
#get the rows from the shapefile order by address ascending
updateTheRows = arcpy.UpdateCursor("C:\\Filename.shp","","","","AddressName A" )  
    i = 0      
    for updateTheRow in updateTheRows:  
        updateTheRow.setValue("FieldNameToUpdate",10000 + i)  
        updateTheRows.updateRow(updateTheRow)  
        i= i+1  
  
    del updateTheRow  
    del updateTheRows  


## Option -- 2
#Right click on the field and choose "Field Calculator", select the Python radio button at the top and #make sure the Show Codeblock box is checked.  Then select and copy lines of code in the first code #block below and put them in the Pre-Logic Script Code block.

rec=0 
def autoIncrement():  
    global rec  
    pStart = 10000 #adjust start value, if req'd  
    pInterval = 1 #adjust interval value, if req'd  
    if (rec == 0):  
       rec = pStart  
    else:  
       rec = rec + pInterval  
    return rec  
