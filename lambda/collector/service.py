# -*- coding: utf-8 -*-
from datetime import datetime
import json
import os
import time

import boto3
import requests


CTA_BUS_API_KEY = os.getenv('CTA_BUS_API_KEY')
CTA_BUS_STOP_ID = os.getenv('CTA_BUS_STOP_ID')
CTA_BUS_PREDICTION_ROUTE = 'http://www.ctabustracker.com/bustime/api/v2/getpredictions'

PREDICTIONS_BUCKET = os.getenv('PREDICTIONS_BUCKET')


def log_file_key(prediction):
    template = '{0}/{1}.json'
    timestamp = str(int(prediction['current_time']))
    return template.format(prediction['route_id'], timestamp)


def to_timestamp(cta_time):
    dt = datetime.strptime(cta_time, "%Y%m%d %H:%M")
    return time.mktime(dt.timetuple())


def cta_bus_predictions(stop_id):
    resp = requests.get(CTA_BUS_PREDICTION_ROUTE, params={
        'stpid': stop_id,
        'key': CTA_BUS_API_KEY,
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


def handler(event, context):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(PREDICTIONS_BUCKET)

    predictions = list(cta_bus_predictions(stop_id=CTA_BUS_STOP_ID))

    if predictions:
        bucket.put_object(Key=log_file_key(predictions[0]),
                          Body=json.dumps(predictions).encode())
