"""
Author: Austin Butler
Date: 11/11/2019
Purpose: Calculate burns and dispersants distances from nearest shoreline and export any data as an excel file

Things to remember before running this script:
- create file geodatabase to store everything
- create text file(s) for definition query(s)
- Store all near shoreline layers in the geodatabase
- Make sure all file paths are correct

"""
# Import arcpy module, open mxd files.
import arcpy, os
from datetime import datetime
startTime = datetime.now()

local_path = "C:\\Temp\\Belo"
z_path = "Z:\\"

# Change these variables every time
claimant_name_path = "PayneM"  # Make sure both the z folder and your local folder have the same name
gdb_name = claimant_name_path + "_AB.gdb" # Make sure your gdb has the same name as the folder + your initials
dq_text_files = ["defq_Theodore.txt"]
scat_layers = ["SCATTheodore"]
# What you want to name the exported Burns/Dispersants feature classes
burns_fc_name = "Burns_Theodore"
# burns_fc_name1 = "Burns_Pensacola"
# burns_fc_name2 = "Burns_Theodore"
dispersants_fc_name = "Dispersants_Theodore"
# dispersants_fc_name1 = "Dispersants_Pensacola"
# dispersants_fc_name2 = "Dispersants_Theodore"

# geodatabase where everything is stored
gdb_path = os.path.join(local_path, claimant_name_path, gdb_name)
print(gdb_path)

# Definition query text file(s) go here
defQfp = os.path.join(local_path, claimant_name_path, dq_text_files[0])
# defQfp1 = os.path.join(local_path, claimant_name_path, dq_text_files[1])
# defQfp2 = os.path.join(local_path, claimant_name_path, dq_text_files[2])
print(defQfp)

# Scat feature(s) file path used for calculate_distances function
scat_fp = os.path.join(gdb_path, scat_layers[0])
# scat_fp1 = os.path.join(gdb_path, scat_layers[1])
# scat_fp2 = os.path.join(gdb_path, scat_layers[2])
print (scat_fp)


# MXD File paths locations needed
BurnsFilePath = os.path.join(z_path, claimant_name_path, claimant_name_path + "_BurnDistances.mxd")
print(BurnsFilePath)
DispersantsFilePath = os.path.join(z_path, claimant_name_path, claimant_name_path + "_DispersantDistances.mxd")
print (DispersantsFilePath)


# open the mxds
BurnsMapDoc = arcpy.mapping.MapDocument(BurnsFilePath)
print("Opened Burns MXD")
DispersantsMapDoc = arcpy.mapping.MapDocument(DispersantsFilePath)
print("Opened Dispersants MXD")


def calculate_distances(layer, scat, excel_name):
    try:
        # run near analysis
        in_feature = layer
        near_feature = scat
        print("Starting Near Analysis")
        arcpy.Near_analysis(in_feature, near_feature, "", "LOCATION", "ANGLE", "GEODESIC")
        print("finished calculating distances")

        # add new field to attribute table
        field_name = "Miles"
        arcpy.AddField_management(layer, field_name, "DOUBLE")
        print("added new field")

        # calculate new field
        meters_to_miles = 0.000621371
        expression = '(  !NEAR_DIST! * {} )'.format(meters_to_miles)
        arcpy.CalculateField_management(layer, field_name, expression, "PYTHON_9.3")
        print("Calculated Miles field")

        # export
        excel_fp = os.path.join(local_path, claimant_name_path)
        print(excel_fp)
        my_excel = excel_fp + "\\" + excel_name + "_Distances.xls"
        arcpy.TableToExcel_conversion(layer, my_excel)
        print(arcpy.GetMessages())

    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))

    except Exception as err:
        print(err.args[0])


# read text file with definition query:
def read_text_file(file_path):
    def_q_list = []
    with open(file_path, "r") as fp:
        for line in fp:
            # line = line.rstrip("\n")
            def_q_list.append(line)
    def_string = "".join(def_q_list)
    return def_string.replace('), ', ')\n')


def get_field_name(layer):
    if layer.name == "In Situ Burns":
        field_name = "Date_"
    else:
        field_name = "FLIGHTDATE"
    return field_name


# Search for Burns/disp layer, then apply definition query, and check if any data are returned. Then export.

def main_function(mxd, text_file_path, scat_layer, feature_class_name):
    for lyr in arcpy.mapping.ListLayers(mxd):
        print("Looking for Burns or dispersants Layer")
        if lyr.name == "In Situ Burns" or lyr.name == "Aerial Dispersants":
            print("Found " + lyr.name)
            if lyr.supports("DEFINITIONQUERY"):
                field = get_field_name(lyr)  # Call field name function to grab correct field name for defq
                query_string = read_text_file(text_file_path)  # call text file function
                lyr.definitionQuery = field + " IN (  " + query_string + " )"
                print("applied definition query")
                # Count how many burns/dispersants are present
                result = arcpy.GetCount_management(lyr)
                layer_count = int(result.getOutput(0))
                # Check if any burns/dispersants are there. If there are, Export to gdb.
                if layer_count > 0:
                    arcpy.FeatureClassToFeatureClass_conversion(lyr, gdb_path, feature_class_name)
                    print(feature_class_name + " exported")
                    new_lyr = gdb_path + "\\" + feature_class_name
                    print(new_lyr)
                    # Call function here that takes the burns/disp and calculates the near distances to the SCAT layer.
                    calculate_distances(new_lyr, scat_layer, feature_class_name)
                else:
                    print("No data was found on those days. Nothing to export")
                break


# Calculate Burns here:
main_function(BurnsMapDoc, defQfp, scat_fp, burns_fc_name)
# main_function(BurnsMapDoc, defQfp1, scat_fp1, burns_fc_name1)
# main_function(BurnsMapDoc, defQfp2, scat_fp2, burns_fc_name2)


BurnsMapDoc.save()
print("Burns mxd saved")

# Calculate Dispersants here:
main_function(DispersantsMapDoc, defQfp, scat_fp, dispersants_fc_name)
# main_function(DispersantsMapDoc, defQfp1, scat_fp1, dispersants_fc_name1)
# main_function(DispersantsMapDoc, defQfp2, scat_fp2, dispersants_fc_name2)

DispersantsMapDoc.save()
print("Dispersants mxd saved")
print datetime.now() - startTime

'''
Step 1: Apply def query on burns or dispersants
Step 2: Export data to gdb
Step 3: Run Near Analysis tool with the following parameters: 
        - Input feature: Projected Burns or dispersants feature class
        - Near Feature: Projected SCAT feature class
        - Location and Angle: applied
        - Method: GEODESIC 
Step 4: Edit burns or dispersants attribute table: 
        - Add new field with the title Miles
        - Set field data type to DOUBLE
Step 5: Run field calculator on Miles:
        - Miles = [NearDist] * 0.000621371
Step 6: Export attribute data as a dBase table or excel file. 


'''
