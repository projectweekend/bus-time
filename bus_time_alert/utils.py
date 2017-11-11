from datetime import datetime
import time


def clean_prediction(dirty_prediction):
    current_time = to_timestamp(dirty_prediction['tmstmp'])
    arrival_time = to_timestamp(dirty_prediction['prdtm'])
    return {
        'stop_id': dirty_prediction['stpid'],
        'route_id': dirty_prediction['rt'],
        'route_direction': dirty_prediction['rtdir'],
        'vehicle_id': dirty_prediction['vid'],
        'current_time': current_time,
        'arrival_time': arrival_time,
        'minutes_to_arrival': (arrival_time - current_time) / 60
    }


def log_file_s3_key(prediction):
    template = '{0}/{1}/{2}.json'
    timestamp = str(int(prediction['current_time']))
    return template.format(prediction['route_id'],
                           prediction['stop_id'],
                           timestamp)


def to_timestamp(cta_time):
    dt = datetime.strptime(cta_time, "%Y%m%d %H:%M")
    return time.mktime(dt.timetuple())


def within_threshold(prediction, threshold):
    minimum = threshold['min']
    maximum = threshold['max']
    arrival = prediction['minutes_to_arrival']
    return arrival >= minimum and arrival <= maximum
