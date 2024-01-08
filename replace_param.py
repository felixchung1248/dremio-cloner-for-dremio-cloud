import json
import sys

# Function to parse key-value pairs from command line arguments
def parse_key_value_pairs(argv):
    params = {}
    for arg in argv[1:]:  # Skip the script name
        key, value = arg.split('=', 1)
        params[key] = value
    return params

# Function to recursively replace PARAM_ values with provided parameters in the JSON structure
def replace_params(obj, params):
    dremio_cloner = obj['dremio_cloner']
    source = dremio_cloner[1]['source']
    source[0]['endpoint'] = params['endpoint']
    source[1]['username'] = params['username']
    source[2]['password'] = params['password']
    source[7]['dremio_cloud_org_id'] = params['dremio_cloud_org_id']
    source[8]['dremio_cloud_project_id'] = params['dremio_cloud_project_id']

    options = dremio_cloner[3]['options']
    options[22]['space.folder.filter'] = params['space.folder.filter']

    vds_filter_names = params['vds.filter.names'].split(',')
    options[35]['vds.filter.names'] = vds_filter_names


# Parse the command-line arguments
parameters = parse_key_value_pairs(sys.argv)

# Extract the JSON file path and remove it from the parameters
json_file_path = parameters.pop('json_file_path', None)

if not json_file_path:
    print("Error: The path to the JSON file must be provided with the key 'json_file_path'.")
    sys.exit(1)

# Read the JSON file
try:
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"Error: The file {json_file_path} was not found.")
    sys.exit(1)

# Replace the PARAM_ values in the JSON data
replace_params(data, parameters)

# Write the modified JSON data back to the file
with open(f"{json_file_path}_filled", 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print(f"Successfully updated {json_file_path}.")