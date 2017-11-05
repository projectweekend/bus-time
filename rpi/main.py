#!/usr/bin/env python
import argparse
from datetime import datetime
import json
import time

import boto3
import requests


CTA_BUS_PREDICTION_ROUTE = 'http://www.ctabustracker.com/bustime/api/v2/getpredictions'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    return parser.parse_args()


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def log_file_s3_key(prediction):
    template = '{0}/{1}.json'
    timestamp = str(int(prediction['current_time']))
    return template.format(prediction['route_id'], timestamp)


def to_timestamp(cta_time):
    dt = datetime.strptime(cta_time, "%Y%m%d %H:%M")
    return time.mktime(dt.timetuple())


def s3_bucket(config):
    s3 = boto3.resource('s3')
    return s3.Bucket(config.s3_bucket)


def cta_bus_predictions(stop_id, api_key, **kwargs):
    resp = requests.get(CTA_BUS_PREDICTION_ROUTE, params={
        'stpid': stop_id,
        'key': api_key,
        'format': 'json'
    }).json()

    bustime_resp = resp.get('bustime-response')
    if bustime_resp is not None:
        predictions = bustime_resp.get('prd')
        if predictions is not None:
            for p in predictions:
                current_time = to_timestamp(p['tmstmp'])
                arrival_time = to_timestamp(p['prdtm'])
                yield {
                    'stop_id': p['stpid'],
                    'route_id': p['rt'],
                    'route_direction': p['rtdir'],
                    'vehicle_id': p['vid'],
                    'current_time': current_time,
                    'arrival_time': arrival_time,
                    'minutes_to_arrival': (arrival_time - current_time) / 60
                }


def show_status(predictions):
    for p in predictions:
        if p['minutes_to_arrival'] >= 5 and  p['minutes_to_arrival'] <= 7:
            print('GREEN LIGHT')
        elif p['minutes_to_arrival'] >= 10 and  p['minutes_to_arrival'] <= 12:
            print('YELLOW')
        else:
            print('RED')
        yield p


def main(cli_args):
    config = load_config(cli_args.config_file)
    predictions = list(show_status(cta_bus_predictions(**config)))
    if predictions:
        bucket = s3_bucket(config)

        kwargs = {
            'Body': json.dumps(predictions).encode(),
            'Key': log_file_s3_key(prediction=predictions[0])
        }
        bucket.put_object(**kwargs)



if __name__ == '__main__':
    main(get_args())
