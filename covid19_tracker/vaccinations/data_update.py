
import requests
import json

URL_VAX_TS = 'https://impfdashboard.de/static/data/germany_vaccinations_timeseries_v2.tsv'
URL_DELIVIERIES = 'https://impfdashboard.de/static/data/germany_deliveries_timeseries_v2.tsv'
URL_VAX_PROGRESS = 'https://impfdashboard.de/static/data/germany_vaccinations_by_state.tsv'
URL_DATA_VERSION = "https://impfdashboard.de/static/data/metadata.json"

FILE_VAX_TS = '../../data/germany_vaccinations_timeseries_v2.tsv'
FILE_DELIVERIES = '../../data/germany_deliveries_timeseries_v2.tsv'
FILE_VAX_PROGRESS = '../../data/germany_vaccinations_by_state.tsv'
FILE_DATA_VERSION = '../../data/germany_vaccinations_version.json'

def get_file(file_url, file_disc):
    r = requests.get(file_url, allow_redirects=True)
    open(file_disc, 'wb').write(r.content)


def load_data_version(json_file):
    with open(json_file) as f:
        v = json.load(f)
    return v

def update_vax_data():
    get_file(URL_VAX_TS, FILE_VAX_TS)
    get_file(URL_DELIVIERIES, FILE_DELIVERIES)
    get_file(URL_VAX_PROGRESS, FILE_VAX_PROGRESS)
    get_file(URL_DATA_VERSION, FILE_DATA_VERSION)
    data_version = load_data_version(FILE_DATA_VERSION)
    print("data fetching sucessful")
    print(f"vaccinations last updated: {data_version['vaccinationsLastUpdated']}")
    print(f"deliveries last updated: {data_version['deliveryLastUpdated']}")


if __name__=="__main__":

    update_vax_data()