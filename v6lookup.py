#!/usr/bin/python3
''' Look up source of IPV6 NFT blocks '''

import re
import requests
import json  # Import the json module
import time
import sys

# Path to the log file
log_file_path = sys.argv[1]

# Regular expression to find IP addresses following "SRC="
ip_address_pattern = r"SRC=((?:\d{1,3}\.){3}\d{1,3}|[0-9a-fA-F:]+)"

# ANSI escape codes for colors
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
RESET = '\033[0m'

def colorize_line(line):
    """Apply color to matching patterns in the line."""
    # Colorize the entire PROTO and DPT key-value pair
    line = re.sub(r'(PROTO=[^\s]+)', f'{RED}\\1{RESET}', line)  # Color 'PROTO=value' in red
    line = re.sub(r'(DPT=[^\s]+)', f'{GREEN}\\1{RESET}', line)  # Color 'DPT=value' in green
    # Only colorize lines that match 'NEW|isp|org|region'
    if re.search(r'NEW|isp|org|region', line, re.IGNORECASE):
        # Apply colors to specific patterns in the line
        line = re.sub(r'(PROTO=[^\s]+)', f'{RED}\\1{RESET}', line)  # Color 'PROTO=value' in red
        line = re.sub(r'(DPT=[^\s]+)', f'{GREEN}\\1{RESET}', line)  # Color 'DPT=value' in green
        return line
    return line  # If it doesn't match, return the line as is

def colorize_geolocation_data(geolocation_info):
    """Colorize geolocation data fields like 'region' and 'isp'."""
    if 'region' in geolocation_info:
        geolocation_info['region'] = f"{YELLOW}{geolocation_info['region']}{RESET}"  # Color 'region' in yellow
    if 'isp' in geolocation_info:
        geolocation_info['isp'] = f"{BLUE}{geolocation_info['isp']}{RESET}"  # Color 'isp' in blue
    return geolocation_info

def query_ip_geolocation(ip_address):
    """Query geolocation for a given IP address using http://ip-api.com/json/"""
    try:
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        if response.status_code == 200:
            return response.json()  # Return the raw JSON data from the response
        else:
            return None
    except requests.RequestException as e:
        print(f"Error querying IP-API for {ip_address}: {e}")
        return None

def extract_ip_addresses_and_geolocate(log_file_path):
    processed_ips = set()  # Set to keep track of processed IP addresses
    try:
        with open(log_file_path, 'r') as file:
            for line in file:
                # The following line is for human reference:
                # grep -Ev 'OUT= MAC='
                # This line should not be addressed programmatically in the script.
                
                # Colorize the line based on grep-like conditions
                colored_line = colorize_line(line)
                if colored_line:
                    print(colored_line)  # Output colorized line

                ip_address_match = re.search(ip_address_pattern, line)
                if ip_address_match:
                    ip_address = ip_address_match.group(1)
                    if ip_address.startswith("fd00:"):  # Skip addresses starting with fd00:
                        print(f"Skipped IP Address: {ip_address}")
                        continue
                    if ip_address not in processed_ips:
                        geolocation_info = query_ip_geolocation(ip_address)
                        if geolocation_info:
                            # Colorize geolocation data for 'region' and 'isp'
                            colorized_geolocation_info = colorize_geolocation_data(geolocation_info)
                            
                            # Print the IP address and the colorized geolocation data
                            print(f"IP Address: {ip_address}, Geolocation Info:")
                            print(f"  Region: {colorized_geolocation_info['region']}")
                            print(f"  ISP: {colorized_geolocation_info['isp']}")
                            
                            # Print the rest of the geolocation data without color
                            for key, value in colorized_geolocation_info.items():
                                if key not in ['region', 'isp']:  # Skip already printed fields
                                    print(f"  {key}: {value}")
                        else:
                            print(f"IP Address: {ip_address}, Geolocation Info: Not found or error")
                        processed_ips.add(ip_address)
    except FileNotFoundError:
        print(f"File {log_file_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the function
extract_ip_addresses_and_geolocate(log_file_path)
