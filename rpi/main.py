#!/usr/bin/env python
import argparse
import json


CTA_BUS_PREDICTION_ROUTE = 'http://www.ctabustracker.com/bustime/api/v2/getpredictions'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file')
    return parser.parse_args()


def load_config(config_file):
    with open(config_file, 'r') as f:
        return json.load(f)


def main(cli_args):
    config = load_config(cli_args.config_file)
    print(config)


if __name__ == '__main__':
    main(get_args())
