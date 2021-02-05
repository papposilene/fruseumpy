#!/usr/bin/env python3
import argparse
import os.path
import csv
import json
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
##import reverse_geocode

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def parse_args():
    parser = argparse.ArgumentParser(description='Convert messy liste-et-localisation-des-musees-de-france csv files to structured file')
    parser.add_argument('-i', '--input', type=str, required=True, help='input messy csv filename')
    #parser.add_argument('-o', '--output', type=str, required=True, help='input structured csv filename')
    parser.add_argument('-v', '--version', action='version', version='1.0')
    return parser.parse_args()

def create_entry():
    return {
        "id": None,
        "osm_id": None,
        "name": None,
        "number": None,
        "street": None,
        "postal_code": None,
        "city": None,
        "country": None,
        "country_code": None,
        "status": None,
        "lat": None,
        "lon": None,
        "website": None,
        "phone": None,
        "fax": None,
        "year": None,
        "stats": None,
        "tags": None,
        "description": None
    }

def main():
    args = parse_args()
    locator = Nominatim(user_agent="fruseum-data/llmf", timeout=10)

    fieldnames = ['id', 'osm_id', 'name', 'number', 'street', 'postal_code', 'city', 'country', 'country_code',
                    'status', 'lat', 'lon', 'website', 'phone', 'fax', 'opening_days', 'closing_days', 'stats', 'tags', 'description']

    with open(args.input, newline='') as csv_inputfile:
        csv_reader = csv.reader(csv_inputfile, delimiter=';', quotechar='|')
        headers = next(csv_reader, None)

        num_rows = 0
        entry = create_entry()

        for row in csv_reader:
            print(f"{bcolors.OKGREEN}Row #", num_rows, f"{bcolors.ENDC}")
            print(f"{bcolors.OKCYAN}Row data: ", row, f"{bcolors.ENDC}")

            entry['id'] = row[1]
            entry['name'] = row[0]

            #print(row[1])
            location = locator.geocode(row[1] + ' ' + row[3], addressdetails=True)
            if hasattr(location, 'raw'):
                print(location.raw)
                json_dump = json.dumps(str(location.raw))
                osmdata = json.loads(json_dump)

                if 'osm_id' in osmdata: entry['osm_id'] = location.raw['osm_id']
                if 'lat' in osmdata: entry['lat'] = location.raw['lat']
                if 'lon' in osmdata: entry['lon'] = location.raw['lon']
                if 'house_number' in osmdata: entry['number'] = location.raw['address']['house_number']
                if 'road' in osmdata: entry['street'] = location.raw['address']['road']
                if 'postcode' in osmdata: entry['postal_code'] = location.raw['address']['postcode']
                if 'village' in osmdata:
                    entry['city'] = location.raw['address']['village']
                elif 'town' in osmdata:
                    entry['city'] = location.raw['address']['town']
                elif 'municipality' in osmdata:
                    entry['city'] = location.raw['address']['municipality']
                elif 'city' in osmdata:
                    entry['city'] = location.raw['address']['city']
                else:
                    entry['city'] = ""
                if 'country' in osmdata: entry['country'] = location.raw['address']['country']
                if 'country_code' in osmdata:  entry['country_code'] = location.raw['address']['country_code']
            else:
                address = row[2].split(' ', 0)
                entry['number'] = address[0]
                entry['street'] = address[1]
                entry['postal_code'] = row[3]
                entry['city'] = row[4]
                entry['country'] = 'France'
                entry['country_code'] = 'fr'
                geoloc = row[15].split(',')
                entry['lat'] = address[0]
                entry['lon'] = address[1]

            entry['phone'] = row[5]
            entry['fax'] = row[6]
            entry['website'] = row[7]

            if row[10] == 'R':
                entry['tags'] = 'unlabel:musee de france'
            else:
                entry['tags'] = 'label:musee de france'

            entry['opening_days'] = row[9]
            entry['closing_days'] = row[8]

            entry['stats'] = entry['stats'] + ';' + 'label-date:' + row[11]
            if row[12]:
                entry['stats'] = entry['stats'] + ';' + 'unlabel-date:' + row[12]

            output_file = './data/liste-et-localisation-des-musees-de-france.csv'
            if os.path.isfile(output_file):
                with open(output_file, 'a+', newline='') as csv_outputfile:
                    csv_writer = csv.DictWriter(csv_outputfile, fieldnames=fieldnames)
                    csv_writer.writerow(entry)
            else:
                with open(output_file, 'a+', newline='') as csv_outputfile:
                    csv_writer = csv.DictWriter(csv_outputfile, fieldnames=fieldnames)
                    csv_writer.writeheader()
                    csv_writer.writerow(entry)

            num_rows += 1
            entry = create_entry()

        print('wrote {} rows.'.format(num_rows))

if __name__ == '__main__':
    main()