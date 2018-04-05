"""Discord Bot Configuration"""
import json

def get_config(fileLocation):
    """Load the config file into memory"""
    with open(fileLocation) as config_file:
        return json.load(config_file)
