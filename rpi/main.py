#!/usr/bin/env python
import argparse
from datetime import datetime
import json
import time

import boto3
import requests


CTA_BUS_PREDICTION_ROUTE = 'http://www.ctabustracker.com/bustime/api/v2/getpredictions'

RED = 'red'
YELLOW = 'yellow'
GREEN = 'green'


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
    s3 = boto3.resource('s3', **config['aws'])
    return s3.Bucket(config['s3_bucket'])


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


def led_status(predictions):
    status = {
        RED: 0,
        YELLOW: 0,
        GREEN: 0
    }
    for p in predictions:
        if p['minutes_to_arrival'] >= 5 and  p['minutes_to_arrival'] <= 7:
            status[GREEN] = 1
        elif p['minutes_to_arrival'] >= 10 and  p['minutes_to_arrival'] <= 12:
            status[YELLOW] = 1
        else:
            status[RED] = 1
    return status


def display(led_status, led_pins):
    for color, status in led_status.items():
        pin = led_pins[color]
        print('Set {0} LED at pin {1} to: {2}'.format(color, pin, status))


def main(cli_args):
    config = load_config(cli_args.config_file)
    predictions = list(cta_bus_predictions(**config))
    display(led_status(predictions), config['led_pins'])

    if predictions:
        bucket = s3_bucket(config)
        kwargs = {
            'Body': json.dumps(predictions).encode(),
            'Key': log_file_s3_key(prediction=predictions[0])
        }
        bucket.put_object(**kwargs)



if __name__ == '__main__':
    main(get_args())
