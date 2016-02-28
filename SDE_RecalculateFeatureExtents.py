## Have hundreds of feature datasets that have incorrect XY entents. So, recalculatatio of Feature #Extent can be done from Feature Class's "Feature Extent" property in ArcCatalog. But to save time by #automating the pressing of the 'Recalculate' button for hundreds of feature datasets that have #incorrect XY entents, Need a tool that can run with an iterator to run over each feature classes.

##if memory serves that was a problem solver when processing on shapefiles were not reflected until ##the shape field index was recalculated.And check the environment settings.Maintain Spatial Index ##(Environment setting or to rebuild Add Spatial Index


def calculate_extents(workspace):  
    arcpy.env.workspace = workspace   
    # Get the user name for the workspace  
    user_name = arcpy.Describe(workspace).connectionProperties.user.lower()  
    print user_name  
  
    # Get a list of all the Feature Classes which the user owns.  
    dataList = arcpy.ListFeatureClasses('{}*'.format(user_name.upper()))  
    print(len(dataList))  
     
    # Next, for feature datasets get all of the datasets and featureclasses  
    # from the list and add them to the master list.  
    for dataset in arcpy.ListDatasets('{}*'.format(user_name.upper()), "Feature"):  
        arcpy.env.workspace = os.path.join(workspace,dataset)  
        dataList += arcpy.ListFeatureClasses()  
  
 
    # reset the workspace  
    arcpy.env.workspace = workspace  
    print('Setting Accept Connections => False')  
    arcpy.AcceptConnections(workspace, False)  
    print('Disconnecting Users {}'.format(arcpy.ListUsers(workspace)))  
    arcpy.DisconnectUser(workspace, "ALL")  
     
    for feature in dataList:  
        while True:  
            print feature  
            try:  
                extent1 = str(arcpy.Describe(feature).extent)  
                arcpy.RecalculateFeatureClassExtent_management(feature)  
                extent2 = str(arcpy.Describe(feature).extent)  
                updated = 'UPDATED'  
                if extent1 == extent2:  updated = 'SAME'  
                print('{}: {} =>\t{}'.format(updated, extent1, extent2))  
                break  
            except arcgisscripting.ExecuteError:  
                print('ERROR -- Attempting to disconnect users')  
                arcpy.DisconnectUser(workspace, "ALL")  
  
    arcpy.AcceptConnections(workspace, True)  
