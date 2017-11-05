#!/usr/bin/env python
import argparse
from datetime import datetime
import json
import time

import boto3
import requests

from utils import (
    clean_prediction,
    log_file_s3_key,
    within_threshold
)


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


def led_status(predictions, arrival_thresholds):
    status = {
        RED: 0,
        YELLOW: 0,
        GREEN: 0
    }
    for p in predictions:
        if within_threshold(p, arrival_thresholds[GREEN]):
            status[GREEN] = 1
        elif within_threshold(p, arrival_thresholds[YELLOW]):
            status[YELLOW] = 1
        else:
            status[RED] = 1
    return status


def s3_bucket(config):
    s3 = boto3.resource('s3', **config['aws'])
    return s3.Bucket(config['s3_bucket'])


def predictions_for_stop(stop_id, api_key):
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
                yield clean_prediction(p)


def predictions_for_route(predictions, route_id):
    for p in predictions:
        if p['route_id'] == route_id:
            yield p


def predictions(stop_id, route_id, api_key, **kwargs):
    for_stop = predictions_for_stop(stop_id, api_key)
    return list(predictions_for_route(for_stop, route_id))


def display(led_status, led_pins):
    for color, status in led_status.items():
        pin = led_pins[color]
        print('Set {0} LED at pin {1} to: {2}'.format(color, pin, status))


def main(cli_args):
    config = load_config(cli_args.config_file)
    arrival_thresholds = config['arrival_thresholds']
    led_pins = config['led_pins']

    predictions_output = predictions(**config)
    display(led_status(predictions_output, arrival_thresholds), led_pins)

    if predictions:
        bucket = s3_bucket(config)
        kwargs = {
            'Body': json.dumps(predictions_output).encode(),
            'Key': log_file_s3_key(prediction=predictions_output[0])
        }
        bucket.put_object(**kwargs)



if __name__ == '__main__':
    main(get_args())
