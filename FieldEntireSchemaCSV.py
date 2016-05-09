import arcpy, traceback, sys, csv
from arcpy import env
env.workspace = u"D:/TCS/ESRI_SCW_Schema.gdb"
outFilePath = u"E:/";

print "Process Started ... ";
try:
    for ds in arcpy.ListDatasets():
        csvFlPath = outFilePath + ds + ".csv"
        with open(csvFlPath, 'wb') as fp:
            a = csv.writer(fp)
            rowDt = [["Feature Class","Feature Type","Field","Alias","Domain","Default Value","Type","Length","Precision","Scale","IsEditable","IsNull","IsRequired"]]
            a.writerows(rowDt)
            for ftCls in arcpy.ListFeatureClasses("","",ds):
                print " Executing for ... " + ds + "/" + ftCls; rowDts = [];
                ftClsType = str(arcpy.Describe(ftCls).shapeType);
                for f in arcpy.ListFields(ftCls):
                    fType = f.type;
                    if fType == "Integer" : fType = "LONG Integer";
                    if fType == "SmallInteger" : fType = "SHORT Integer";
                    if fType == "Single" : fType = "Single (Float)";
                    #print fType
                    rowDt = [ftCls,ftClsType, f.name, f.aliasName, f.domain, f.defaultValue, fType, f.length, f.precision,
                             f.scale,f.editable, f.isNullable, f.required];
                    rowDts.append(rowDt);
                print " Executed for ... " + ds + "/" +  ftCls;
                a.writerows(rowDts);

except Exception as ex: print traceback.format_exc();
print "Process Completed ... "; sys.exit();
