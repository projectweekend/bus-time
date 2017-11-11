import requests

from utils import clean_prediction


CTA_BUS_PREDICTION_ROUTE = 'http://www.ctabustracker.com/bustime/api/v2/getpredictions'


def _predictions_for_stop(stop_id, api_key):
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


def _predictions_for_route(predictions, route_id):
    for p in predictions:
        if p['route_id'] == route_id:
            yield p


def predictions(stop_id, route_id, api_key, **kwargs):
    for_stop = _predictions_for_stop(stop_id, api_key)
    return _predictions_for_route(for_stop, route_id)
