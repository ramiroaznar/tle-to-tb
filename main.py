import sat_utils as sats
import data_utils as data
import datetime as dt
import click

@click.command()
@click.option('--interval', default=10, help='Interval (in minutes) for data extraction')
@click.option('--format', default='ndjson', help='Format for saving data')
@click.option('--save', default=True, help='Save data')
@click.option('--send', default=True, help='Send data to Tinybird')

def main(interval, format, save, send):
    # Specify start and end times for data extraction
    start_time = dt.datetime.utcnow()
    end_time = start_time + dt.timedelta(minutes=interval)

    # Build URL for TLE data
    tle_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=planet&FORMAT=tle"

    # Fetch TLE data from the URL
    satellites = sats.get_satellite_data_from_url(tle_url)

    # Convert TLE to coordinates for all satellites
    satellite_data = sats.convert_tle_to_coordinates(satellites, start_time, end_time)

    # Save data
    if save:
        data.save_data(satellite_data, format=format, filename='satellite_data')

    # Send data to Tinybird
    if send:
        data.send_satellite_data(filename='satellite_data.ndjson')

if __name__ == "__main__":
    main()