 # csv status reporting
import csv

fieldnames = ['sarif_file', 'level', 'message', "extra_info"]

warning_set = {
  "success" : 0,
  "zero_results" : 0,
  "input_sarif_missing" : 0
}

#
# Setup csv status writer
#
def setup_csv_writer(filename):
  with open(filename+'.csv', 'w', newline='') as file:
    # global in module as singleton alt
      global global_filename
      global_filename = filename
      csv_writer = csv.DictWriter(file, fieldnames)
      csv_writer.writeheader()

#
# csv status write - one line for errors
#
def csv_write(data):
  with open(global_filename+'.csv', 'a', newline='') as file:
      csv_writer = csv.DictWriter(file, fieldnames)
      csv_writer.writerow(data)

#
# csv status write - all at once for type of warnings that can 
# happen multiple times
# and want success message last
#
def csv_write_warnings():
  with open(global_filename+'.csv', 'a', newline='') as file:
      csv_writer = csv.DictWriter(file, fieldnames)
      if warning_set["input_sarif_missing"] != 0:
        csv_writer.writerow(input_sarif_missing)
        #reset in case later different types of warnings can be accumulated
        input_sarif_missing["extra_info"] = "Missing: "
        warning_set["input_sarif_missing"] = 0
      if warning_set["success"] != 0:
        csv_writer.writerow(success)

def setup_status_filenames(sarif_file_name):
  success["sarif_file"] = sarif_file_name
  zero_results["sarif_file"] = sarif_file_name
  input_sarif_extra["sarif_file"] = sarif_file_name
  input_sarif_missing["sarif_file"] = sarif_file_name
  unknown_sarif_parsing_shape["sarif_file"] = sarif_file_name
  unknown["sarif_file"] = sarif_file_name

success = {
  "sarif_file": "",
  "level": "SUCCESS",
  "message": "File successfully processed."
}

zero_results = {
  "sarif_file": "",
  "level": "WARNING",
  "message": "Zero results seen in sarif file."
}

input_sarif_missing = {
  "sarif_file": "",
  "level": "WARNING",
  "message": "Input sarif is missing neccesary properties.",
  "extra_info" : "Missing: "
}

 # file load error can happen on either sarif file or scan-spec.json
file_load_error = {
  "file": "",
  "level": "ERROR",
  "message": "Could not load file."
}

input_sarif_extra  = {
  "sarif_file": "",
  "level": "ERROR",
  "message": "Input sarif contains extra unneccesary properties."
}

unknown_sarif_parsing_shape = {
  "sarif_file": "",
  "level": "ERROR",
  "message": "Error matching expected sarif format to actual input sarif shape.",
  "extra_info" : ""
}

unknown = {
  "sarif_file": "",
  "level": "ERROR",
  "message": "Error details currently undiagnosed. Assess log file for more information."
}