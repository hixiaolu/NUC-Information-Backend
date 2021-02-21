import copy
import json
import time

import requests

labels = {
    'app': 'nuc-info',
    'type': 'api',
}

session = requests.session()


def log(route: str, processing_time: int, code: int, cached: bool, path: str):
    local_labels = copy.deepcopy(labels)
    local_labels['route'] = str(route)
    local_labels['code'] = str(code)
    local_labels['cached'] = str(cached)
    ns = 1e9
    ts = str(int(time.time() * ns))
    payload = json.dumps({'processingTime': processing_time, 'path': path})
    stream = {
        "stream": local_labels,
        "values": [[ts, payload]],
    }
    session.post('http://tencent-gz.dreace.top:3100/loki/api/v1/push', json={"streams": [stream]})


def exception(content: str):
    labels_local = {
        'app': 'nuc-info',
        'type': 'exception',
    }
    ns = 1e9
    ts = str(int(time.time() * ns))
    stream = {
        "stream": labels_local,
        "values": [[ts, content]],
    }
    session.post('http://tencent-gz.dreace.top:3100/loki/api/v1/push', json={"streams": [stream]})
