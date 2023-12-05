
import logging
import ephem
import requests
import datetime as dt
from progress.bar import Bar

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Satellite:
    def __init__(self, line1, line2, line3):
        self.line1 = line1
        self.line2 = line2
        self.line3 = line3

def get_satellite_data_from_url(url):
    logger.info(f"Fetching TLE data from URL: {url}")

    tle = requests.get(url).text
    lines = tle.split('\n')
    satellites = []
    satellite_data = []
    num_lines = len(lines) - 1

    with Bar('Getting TLE data', max=num_lines/3) as bar:
        for i in range(0, num_lines, 3):
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip()
            line3 = lines[i + 2].strip()

            satellite = Satellite(line1, line2, line3)
            satellites.append(satellite)

            # Create ephem satellites from the TLE data
            for satellite in satellites:
                satellite_data.append(ephem.readtle(satellite.line1, satellite.line2, satellite.line3))
            bar.next()

    logger.info(f"Found {len(satellites)} satellites")
    return satellite_data

def convert_tle_to_coordinates(satellites, start_time, end_time, interval_seconds=60):
    logger.info("Converting TLE to coordinates for all satellites")

    # Generate time range
    times = [start_time + dt.timedelta(seconds=i) for i in range(0, int((end_time - start_time).total_seconds()), interval_seconds)]

    # Extract latitude, longitude, and timestamps for all satellites
    satellite_data = []
    num_satellites = len(satellites)

    with Bar('Extracting coordinates and timestamps by satellite', max=num_satellites) as bar:
        for satellite in satellites:
            latitudes = []
            longitudes = []
            timestamps = []

            for time in times:
                satellite.compute(time)
                latitudes.append(round(satellite.sublat/ephem.degree,2))
                longitudes.append(round(satellite.sublong/ephem.degree,2))
                timestamps.append(time.strftime("%Y-%m-%d %H:%M:%S"))

            satellite_data.append({
                'satellite_name': satellite.name,
                'latitudes': latitudes,
                'longitudes': longitudes,
                'timestamps': timestamps
            })
            bar.next()

    return satellite_data