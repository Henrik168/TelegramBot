import requests
import json


def http_request(url: str, params=None, files=None) -> dict:
    """

    :param url:
    :param params:
    :param files:
    :return:
    """
    try:
        response = requests.get(url, params=params, files=files, timeout=10)
    except (requests.ReadTimeout, requests.HTTPError, requests.Timeout, requests.ConnectionError) as e:
        raise ConnectionError(f'Requests Error ({e}) in url: {url}, with params: {params}, with files: {files} ')

    try:
        result = response.json()
    except json.JSONDecodeError as e:
        raise ConnectionError(f'JSON Decode Error ({e}) in response: {response} ')

    return result


def snap_request(url: str):
    """
    Download a Snapshot from Webcam
    :param url:
    :return:
    """
    try:
        response = requests.get(url)
    except (requests.ReadTimeout,
            requests.HTTPError,
            requests.Timeout,
            requests.ConnectionError,
            requests.exceptions.MissingSchema) as e:
        raise ConnectionError(f'Requests Error ({e}) in url: {url}')

    if response.status_code != 200:
        raise RuntimeError(f'Failed to fetch image from: {url}')
    return response.content

