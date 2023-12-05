import logging
import csv
import json
import requests as req
import os


# Get TOKEN from environment variable
TB_TOKEN = os.environ.get('TB_TOKEN')
if TB_TOKEN is None:
    raise Exception('TB_TOKEN environment variable not found')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_satellite_data(filename, token=TB_TOKEN):
    logger.info(f"Sending satellite events to Tinybird")

    params = {
        'name': 'satellite_data',
        'token': token,
    }

    data = read_ndjson(filename)
    logging.info(f"Sending {len(data)} data to Tinybird")
        
    try:
        r = req.post('https://api.tinybird.co/v0/events', params=params, data=data)
        r.raise_for_status()
    except req.exceptions.HTTPError as e:
        logger.error(f"Error sending data to Tinybird: {e}")
        raise Exception(f"Error sending data to Tinybird: {e}")

def save_to_csv(data, filename='output.csv'):
    logger.info(f"Saving data to CSV file: {filename}")
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['satellite_name', 'timestamp', 'latitude', 'longitude']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for satellite in data:
            for i in range(len(satellite['latitudes'])):
                writer.writerow({
                    'satellite_name': satellite['satellite_name'],
                    'timestamp': satellite['timestamps'][i],
                    'latitude': satellite['latitudes'][i],
                    'longitude': satellite['longitudes'][i]
                })

def read_ndjson(filename):
    logger.info(f"Reading NDJSON file: {filename}")
    with open(filename, 'r') as ndjsonfile:
        data = []
        for line in ndjsonfile:
            data.append(json.loads(line))
        return '\n'.join([json.dumps(i) for i in data])

def save_to_ndjson(data, filename='output.ndjson'):
    logger.info(f"Saving data to NDJSON file: {filename}")
    with open(filename, 'w') as ndjsonfile:
        for satellite in data:
            for i in range(len(satellite['latitudes'])):
                ndjsonfile.write(json.dumps({
                    'satellite_name': satellite['satellite_name'],
                    'timestamp': satellite['timestamps'][i],
                    'latitude': satellite['latitudes'][i],
                    'longitude': satellite['longitudes'][i]
                }) + '\n')

def save_data(data, format='csv', filename='output'):
    if format == 'csv':
        save_to_csv(data, filename=f'{filename}.csv')
    elif format == 'ndjson':
        save_to_ndjson(data, filename=f'{filename}.ndjson')
    else:
        raise Exception(f"Invalid format: {format}")