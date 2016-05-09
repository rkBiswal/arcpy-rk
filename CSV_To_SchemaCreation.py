import arcpy, traceback, sys, os, csv
from arcpy import env

### Params -  Command Line  ###
workSpacePath = arcpy.GetParameterAsText(0)
csvSchemaFilePath = arcpy.GetParameterAsText(1)

### Params -  In Line Code  ###
workSpacePath = u'D:\\TCS\\IMISGIS_DMA0500.gdb'  ## Can be FGDB Path / SDE connection file Path  u'D:\\TCS\\IMISGIS_DMA0500.gdb'
csvSchemaFilePath = u'E:\\'   ## Folder Path containing all the CSV files DataSet wise  u'E:\\'

indexFtCls = 0; indexFtClsType = 1; indexFld = 2; indexFldAls = 3; indexDomain = 4;
indexDfVal = 5; indexType = 6; indexLen = 7; indexPrsn = 8;
indexScale = 9; indexIsEdit = 10; indexIsNull = 11; indexIsReq = 12;

workingDirPath = os.getcwd(); print workingDirPath;


#sptRef = arcpy.SpatialReference("WGS 1984 UTM Zone 18N");
sptRef = arcpy.SpatialReference(3857)

try:
    env.workspace = workSpacePath
except Exception as ex:
    print traceback.format_exc();

def getFieldType(_fldType):
    if _fldType == None or len(_fldType) == 0 or _fldType.upper() == 'OID' or _fldType.upper() == 'Geometry'.upper(): return None
    elif _fldType.upper() in ('Integer'.upper(),'LONG Integer'.upper()): return "LONG"
    elif _fldType.upper() in ('SmallInteger'.upper(),'SHORT Integer'.upper()): return "SHORT"
    elif _fldType.upper() in ('Single'.upper(),'Single (Float)'.upper(), 'Single Float'.upper()): return "FLOAT"
    elif _fldType.upper() in ('String'.upper()): return "TEXT"
    else: return _fldType.upper()

    
print "Process Started ... ";
try:
    _lstDs = [str(x).upper() for x in arcpy.ListDatasets()] if  arcpy.ListDatasets() != None else []
    _csvFiles = [x for x in os.listdir(csvSchemaFilePath) if x.endswith('.csv')]

    for _csvFile in _csvFiles:
        ds = _csvFile.replace('.csv','')
        if str(ds).upper() not in _lstDs: #Create DataSet
            print "Executing for Data Set - " + ds
            arcpy.CreateFeatureDataset_management(env.workspace, ds, sptRef)

        ## Create Feat Class in Created/Existing DataSet  -- Not in Use
        headerRow = None;
        with open(os.path.join(csvSchemaFilePath, _csvFile), 'rb') as f:
            reader = csv.reader(f);
            for row in reader:
                headerRow = row; break;
        print headerRow;

        _tmpFtCls = None;  # To hv a back-up Cls Name for Compare
        _lstFtCls = [str(x).upper() for x in arcpy.ListFeatureClasses("","", ds)]
        with open(os.path.join(csvSchemaFilePath, _csvFile), 'rb') as f:
            reader = csv.reader(f); i =0; _lstFlds = [];
            for row in reader:
                if i != 0:
                    try:
                        _fldName = str(row[indexFld])
                        _fldType = getFieldType(row[indexType])
                        _isNull = 'NULLABLE' if bool(row[indexIsNull]) else 'NON_NULLABLE'
                        _isReq = 'REQUIRED' if bool(row[indexIsReq]) else 'NON_REQUIRED'
                        _hasDfVal = False; _dfVal = None;
                        if row[indexDfVal] != None: _hasDfVal = len(str(row[indexDfVal])) > 0;
                        if _hasDfVal:
                            if _fldType in ('FLOAT','DOUBLE'): _dfVal = float(str(row[indexDfVal]))
                            elif _fldType in ('SHORT','LONG'): _dfVal = int(float(str(row[indexDfVal])))
                            else: _dfVal = str(row[indexDfVal])
                            
                        if row[indexFtCls] != _tmpFtCls:  ## New Ft Cls Row
                            if _tmpFtCls != None : print " Executed for ... " + ds + "/" + _tmpFtCls;
                            print " Started for ... " + ds + "/" +  str(row[indexFtCls]);
                            if str(row[indexFtCls]).upper() not in _lstFtCls:
                                arcpy.CreateFeatureclass_management(os.path.join(env.workspace, ds), row[indexFtCls], row[indexFtClsType],"","","", sptRef)
                                _lstFtCls.append(str(row[indexFtCls]).upper());

                            _tmpFtCls = row[indexFtCls];
                            
                            _lstFlds = [str(x.name).upper() for x in arcpy.ListFields(ds+"/"+row[indexFtCls])]
                            if (_fldName.upper() not in _lstFlds) and (_fldType != None):
                                arcpy.AddField_management(_tmpFtCls, _fldName, _fldType, row[indexPrsn], row[indexScale], row[indexLen], row[indexFldAls], _isNull, _isReq)
                                _lstFlds.append(_fldName.upper());
                                if _hasDfVal:
                                    arcpy.AssignDefaultToField_management(_tmpFtCls, _fldName, _dfVal)
                                
                        else:  ## Current Ft Cls Rows
                            if (_fldName.upper() not in _lstFlds) and (_fldType != None):
                                arcpy.AddField_management(_tmpFtCls, _fldName, _fldType, row[indexPrsn], row[indexScale], row[indexLen], row[indexFldAls], _isNull, _isReq)
                                _lstFlds.append(_fldName.upper());
                                if _hasDfVal:
                                    arcpy.AssignDefaultToField_management(_tmpFtCls, _fldName, _dfVal)
                                
                    except Exception as ex:
                        print traceback.format_exc();
                else:  ## Header Row
                    i+=1;

except Exception as ex:
    print traceback.format_exc();
print "Process Completed ... ";
sys.exit();


