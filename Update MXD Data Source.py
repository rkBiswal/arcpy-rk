## This can be added directly to ArcGIS Toolbox as a Script Tool ##

import sys, os, datetime;
import webbrowser;
import xml.dom.minidom as DOM;
import arcpy;
from arcpy import env;
env.overwriteOutput = True;

optAction = arcpy.GetParameterAsText(0)
optMxd = arcpy.GetParameterAsText(1)
mxdFile = arcpy.GetParameterAsText(2)
sdeConn = arcpy.GetParameterAsText(3)
agsConn = arcpy.GetParameterAsText(4)
lstSrvCap = arcpy.GetParameterAsText(5).split(';')
#arcpy.AddMessage(lstSrvCap)

## Process Log
log_path = os.path.dirname(mxdFile) + "\\log_" + datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d_%H%M%S') + ".txt";
txt_log = open(log_path,'a');
txt_log_pbl_Wrn = open(log_path.replace('log_','log_Warnings_'),'a');
txt_log_pbl_Err = open(log_path.replace('log_','log_Errors_'),'a');
def Log(_msg):
    txt_log.write(datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d %H:%M:%S') + " :: " + _msg + "\n");
def LogPublishWrn(_msg):
    txt_log_pbl_Wrn.write(_msg + "\n");
def LogPublishErr(_msg):
    txt_log_pbl_Err.write(_msg + "\n");
Log("Process Started ...");

# Validation :: Start ...
if (sdeConn == "")& (optAction in ["MXD Data Source Update","MXD Data Source Update & Service Publish"]):
    Log(" SDE Connection File is Invalid .. ");
    arcpy.AddMessage(" SDE Connection File is Invalid .. ");
    
if (agsConn == "")& (optAction in ["Map Service Publish / Update","MXD Data Source Update & Service Publish"]):
    Log(" AGS Connection File is Invalid .. ");
    arcpy.AddMessage(" AGS connection File is Invalid .. ");
        
# Validations :: End ...

## MXD Data Source Change :: Start ##

# MXD Each LAyer wise Validate Function:: Start ##

# MXD Each LAyer wise Validate Function:: End ##

if(optMxd == "Selected MXD") & (optAction in ["MXD Data Source Update","MXD Data Source Update & Service Publish"]):
    if (sdeConn != ""):
        mxd = arcpy.mapping.MapDocument(mxdFile)
        try:
            mxd.findAndReplaceWorkspacePaths("",sdeConn,True);
            mxd.save();
            del mxd;
        except arcpy.ExecuteError: Log(arcpy.GetMessages(2));
        except Exception as e: Log(str(e));

if(optMxd == "All MXDs") & (optAction in ["MXD Data Source Update","MXD Data Source Update & Service Publish"]):
    if (sdeConn != ""):
        env.workspace = os.path.dirname(mxdFile);
        lstMxd = arcpy.ListFiles("*.mxd");
        for mxd in lstMxd:
            mxdPath = env.workspace + "\\" + mxd;
            try:
                mxd = arcpy.mapping.MapDocument(mxdPath);
                mxd.findAndReplaceWorkspacePaths("",sdeConn,True);
                mxd.save();
                del mxd;
            except arcpy.ExecuteError: Log(arcpy.GetMessages(2));
            except Exception as e: Log(str(e));

## MXD Data Source Change :: End ##

## MXD Publish to AGS Manager :: Start ##
def PublishMXD(_mxdFile):
    Log("MXD File Path : " + _mxdFile);
    sddraft = _mxdFile.replace(".mxd",".sddraft");
    if (os.path.isfile(sddraft)): os.remove(sddraft);
    sd = _mxdFile.replace(".mxd",".sd");
    Log(sd);
    if (os.path.isfile(sd)): os.remove(sd);
    srvName = os.path.basename(_mxdFile.replace(".mxd",""));
    try:
        arcpy.mapping.CreateMapSDDraft(_mxdFile, sddraft, srvName, 'ARCGIS_SERVER', agsConn,
                                       False, None, srvName + " Service", '');
        doc = DOM.parse(sddraft);

        if 'FeatureServer' in lstSrvCap:
            for key in doc.getElementsByTagName('Key'):           
                if key.firstChild.data == 'maxRecordCount': key.nextSibling.firstChild.data = 9000  ## default value is 1000
                if key.firstChild.data == 'MinInstances': key.nextSibling.firstChild.data = 2  ## default value 1
                if key.firstChild.data == 'MaxInstances': key.nextSibling.firstChild.data = 4  ## default value 2

        if lstSrvCap != ['']:
            for srvInfo in doc.getElementsByTagName('TypeName'):
                if srvInfo.firstChild.data in lstSrvCap:
                    srvInfo.parentNode.getElementsByTagName('Enabled')[0].firstChild.data = 'true'

        # save changes
        #if os.path.exists(sddraft): os.remove(sddraft)
        f = open(sddraft,"w");
        doc.writexml(f);
        f.close();
        # Analyze the new sddraft for errors.
        analysis = arcpy.mapping.AnalyzeForSD(sddraft);
        if analysis['errors'] == {}:
            arcpy.StageService_server(sddraft, sd);
            arcpy.UploadServiceDefinition_server(sd, agsConn);
            if (os.path.isfile(sd)): os.remove(sd);
        else:
            LogPublishErr("Service publication failed: Errors during Analysis.");
            LogPublishErr(_mxdFile);
            for ((message, code), layerlist) in analysis['errors'].iteritems():
                for layer in layerlist:
                    LogPublishErr(message + ", (Code " + code + ") applies to:" + layer.name);
        # Warnings Log ...
        if analysis['warnings'] != {}:
            LogPublishWrn("Service publish : Warnings during Analysis.");
            LogPublishWrn(_mxdFile);
            for ((message, code), layerlist) in analysis['warnings'].iteritems():
                for layer in layerlist:
                    LogPublishWrn(message + ", (Code " + code + ") applies to:" + layer.name);
    except arcpy.ExecuteError: Log(arcpy.GetMessages(2));
    except Exception as e: Log(str(e));

if(optMxd == "Selected MXD") & (optAction in ["Map Service Publish / Update","MXD Data Source Update & Service Publish"]):
    if (agsConn != ""): PublishMXD(mxdFile);

if(optMxd == "All MXDs") & (optAction in ["Map Service Publish / Update","MXD Data Source Update & Service Publish"]):
    if(agsConn != ""):
        env.workspace = os.path.dirname(mxdFile);
        lstMxd = arcpy.ListFiles("*.mxd");
        for mxd in lstMxd: PublishMXD(env.workspace + "\\" + mxd);

## MXD Publish to AGS Manager :: End ##
Log("Process Completed ... ");
if(os.path.isfile(log_path)):
    txt_log.flush(); txt_log.close(); webbrowser.open(log_path); 
if(os.path.isfile(log_path.replace('log_','log_Warnings_'))):
    txt_log_pbl_Wrn.flush(); txt_log_pbl_Wrn.close(); webbrowser.open(log_path.replace('log_','log_Warnings_'));
if(os.path.isfile(log_path.replace('log_','log_Errors_'))):
    txt_log_pbl_Err.flush(); txt_log_pbl_Err.close(); webbrowser.open(log_path.replace('log_','log_Errors_')); 
