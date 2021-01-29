"""
Author: Austin Butler
Date: 12/9/2019
Purpose: Create Sample Maps and export them to PDF

Things to remember before running this script:
- Make sure you have right map extent set up
- Make sure Scale bar looks good
- Make sure to add any badging location labels
- Make sure you save all definition querys as text files in local folder
- MXD is run off the z folder. Defq txt stored locally.

"""
import arcpy, os
from datetime import datetime
startTime = datetime.now()

local_path = "C:\\Temp\\Belo"
z_path = "Z:\\"
claimant_name_folder = "SampleMaps"  # Name of claimant local folder and z folder. Make sure they are the same name
location_title = "Biloxi"  # The location name you need for the map title ex. "Biloxi"
dq_text_file = "DefQ.txt"  # the name of the definition query text file. Save this locally
mxd_name = "SampleMaps.mxd"  # the full name of the mxd. Make sure to include .mxd extension


defQfp = os.path.join(local_path, claimant_name_folder, dq_text_file) # file path to the definition query.
print(defQfp)
SampleMapsPath = os.path.join(z_path, claimant_name_folder, mxd_name) # file path to the mxd.
print(SampleMapsPath)

SampleMapsDoc = arcpy.mapping.MapDocument(SampleMapsPath)
print("Opened" + mxd_name)


# Check def q if there is a trailing comma at the end. If there is, remove it
def check_def_q(dq):
    if dq[-1] == ",":
        return dq[: -1]
    else:
        return dq


# Read definition query text file
def read_text_file(file_path):
    def_q_list = []
    with open(file_path, "r") as fp:
        for line in fp:
            def_q_list.append(line)
    def_string = "".join(def_q_list).strip()
    definition_query = check_def_q(def_string)
    return definition_query.replace('), ', ')\n')


# Field name used for definition query
def get_field_name(layer):
    if layer.name == "Personal Breathing Zone Sampling GSD" or layer.name == "Branch Air Sampling GSD":
        field_name = "Sample_Date"
    else:
        field_name = "Measure_Date"
    return field_name


def change_map_title(mxd, layer):
    if layer.name == "BranchSampling":
        title = "Branch Air Monitoring and Sampling\nCollected on Claimant Days - " + location_title
    elif layer.name == "Personal Breathing Zone Sampling GSD":
        title = "Personal Breathing Zone Sampling\nCollected on Claimant Days - " + location_title
    elif layer.name == "CommunitySampling":
        title = "Community Air Monitoring and Sampling\nCollected During the Response - " + location_title
    elif layer.name == "Water Chemistry Sampling GSD":
        title = "Water Chemistry Sampling\nWithin 1 Meter from Surface - " + location_title
    else:
        title = "title"

    title_item = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "title")[0]
    name_item = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "name")[0]
    title_item.text = title
    name_item.text = claimant_name_folder[:-1]
    title_item.elementPositionX = 11.1877
    title_item.elementPositionY = 10.6926


def export_pdf(mxd, layer):
    print("Exporting " + layer.name)
    export_fp = os.path.join(local_path, claimant_name_folder)
    # Remove any spaces in location title and remove "/" if there are two locations in location title
    location = location_title.replace(" ", "")
    if "/" in location:
        location = location.replace("/", "")

    if layer.name == "BranchSampling":
        file_name = "BranchAir"
        arcpy.mapping.ExportToPDF(mxd,
                                  export_fp + "\\" + claimant_name_folder + "_" + file_name + location + ".pdf")
    elif layer.name == "CommunitySampling":
        file_name = "CommunityAir"
        arcpy.mapping.ExportToPDF(mxd,
                                  export_fp + "\\" + claimant_name_folder + "_" + file_name + location + ".pdf")
    elif layer.name == "Personal Breathing Zone Sampling GSD":
        file_name = "PersonalBreathingZoneSampling"
        arcpy.mapping.ExportToPDF(mxd,
                                  export_fp + "\\" + claimant_name_folder + "_" + file_name + location + ".pdf")
    elif layer.name == "Water Chemistry Sampling GSD":
        file_name = "WaterChemistrySampling"
        arcpy.mapping.ExportToPDF(mxd,
                                  export_fp + "\\" + claimant_name_folder + "_" + file_name + location + ".pdf")


def apply_def_q(layer, txtfp):
    if layer.supports("DEFINITIONQUERY"):
        field = get_field_name(layer)
        query_string = read_text_file(txtfp)
        layer.definitionQuery = field + " IN (  " + query_string + " )"
    print("applied definition query on " + layer.name)


def all_lyrs_off(mxd):
    for lyr in arcpy.mapping.ListLayers(mxd)[0]:
        lyr.visible = False


def main_function(mxd, text_file_path):
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    layers = arcpy.mapping.ListLayers(df)
    all_lyrs_off(mxd)
    mainlayers = arcpy.mapping.ListLayers(mxd, "MainLayers", df)[0]
    mainlayers.visible = True
    for l in layers:
        if l.isGroupLayer and l.name == "MainLayers":
            glayers = arcpy.mapping.ListLayers(l)
            for lyr in glayers:
                if not lyr.isGroupLayer:
                    if lyr.name == "Personal Breathing Zone Sampling GSD" or lyr.name == "Branch Air Sampling GSD"\
                     or lyr.name == "Branch Air Monitoring GSD":
                        apply_def_q(lyr, text_file_path)
                    else:
                        print("No def q needed for " + lyr.name)
            for lyr in glayers:
                lyr.visible = True
                if lyr.name == "BranchSampling":
                    bSamplinglyr = arcpy.mapping.ListLayers(mxd, "Branch Air Sampling GSD", df)[0]
                    bSamplinglyr.visible = True
                    bMonitoringlyr = arcpy.mapping.ListLayers(mxd, "Branch Air Monitoring GSD", df)[0]
                    bMonitoringlyr.visible = True
                    change_map_title(mxd, lyr)
                    export_pdf(mxd, lyr)
                    lyr.visible = False
                elif lyr.name == "CommunitySampling":
                    cSamplinglyr = arcpy.mapping.ListLayers(mxd, "Community Air Sampling GSD", df)[0]
                    cSamplinglyr.visible = True
                    cMonitoringlyr = arcpy.mapping.ListLayers(mxd, "Community Air Monitoring GSD", df)[0]
                    cMonitoringlyr.visible = True
                    change_map_title(mxd, lyr)
                    export_pdf(mxd, lyr)
                    lyr.visible = False
                elif lyr.name == "Personal Breathing Zone Sampling GSD" or lyr.name == "Water Chemistry Sampling GSD":
                    change_map_title(mxd, lyr)
                    export_pdf(mxd, lyr)
                    lyr.visible = False
                else:
                    pass
    # Set title and name back to defaults.
    title = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "title")[0]
    name = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "name")[0]
    title.text = "title"
    name.text = "name"


# Run function
main_function(SampleMapsDoc, defQfp)

SampleMapsDoc.save()
print("mxd saved")
arcpy.RefreshActiveView()
del SampleMapsDoc

print datetime.now() - startTime
'''
STEP 1: Apply def query on personal breathing, and branch air (not community air or water sampling)
STEP 2: Turn on layers one by one. 
STEP 3: Change title text based on layer
STEP 4: Export to PDFs

'''