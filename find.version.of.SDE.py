import arcpy
##Use the release property to find the geodatabase release:
arcpy.Describe("Database Connections\\test.sde").release

##Use the currentRelease property to find out if the geodatabase is current:
arcpy.Describe("Database Connections\\test.sde").currentRelease

##With service pack updates the geodatabase version typically does not
#change but we do sometimes update geodatabase internals such as stored procedures. You can use the currentRelease property to determine
#if stored procedures may have been updated at the service pack and thus
#need to be updated on your server. The currentRelease property compares the
#version of Desktop (or Server) you are using to run Python to the geodatabase
#you are describing.
