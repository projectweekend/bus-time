#!/usr/bin/env python
import argparse
import json

import boto3

import cta
from utils import log_file_s3_key, within_threshold


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


def display(led_status, led_pins):
    for color, status in led_status.items():
        pin = led_pins[color]
        print('Set {0} LED at pin {1} to: {2}'.format(color, pin, status))


def main(cli_args):
    config = load_config(cli_args.config_file)
    arrival_thresholds = config['arrival_thresholds']
    led_pins = config['led_pins']

    predictions = list(cta.predictions(**config))
    display(led_status(predictions, arrival_thresholds), led_pins)

    if predictions:
        bucket = s3_bucket(config)
        kwargs = {
            'Body': json.dumps(predictions).encode(),
            'Key': log_file_s3_key(prediction=predictions[0])
        }
        bucket.put_object(**kwargs)



if __name__ == '__main__':
    main(get_args())
