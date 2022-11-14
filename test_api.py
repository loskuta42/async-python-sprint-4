from http import HTTPStatus

import requests


def test_create_short_url(client):
    response = client.post(
        '/api/v1/short_url/',
        json={
            'origin_url': 'http://ya.ru'
        }
    )
    assert response.status_code == HTTPStatus.CREATED
    assert 'short_url' in response.json()


def test_create_multi_short_url(client):
    response = client.post(
        '/api/v1/short_url/shorten',
        json=[
            {'origin_url': 'http://ya.ru'},
            {'origin_url': 'http://ya.ru'},
        ]
    )
    assert response.status_code == HTTPStatus.CREATED
    results = response.json()
    assert isinstance(results, list)
    assert len(results) == 2
    for result in results:
        assert isinstance(result, dict)
        assert result.get('short_form')
        assert result.get('short_url')


def test_blocking(client_with_middleware):
    response = client_with_middleware.post(
        '/api/v1/short_url/shorten',
        json=[
            {'origin_url': 'http://ya.ru'},
            {'origin_url': 'http://ya.ru'},
        ]
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_by_url_id(start_server):
    post_response = requests.post(
        'http://127.0.0.1:8080/api/v1/short_url/',
        json={
            'origin_url': 'http://ya.ru'
        }
    )
    url = post_response.json().get('short_url')
    get_response = requests.get(url)
    assert get_response.history[0].status_code == HTTPStatus.TEMPORARY_REDIRECT
    assert get_response.history[0].headers.get('Location') == 'http://ya.ru'


def test_delete(start_server):
    post_response = requests.post(
        'http://127.0.0.1:8080/api/v1/short_url/',
        json={
            'origin_url': 'http://ya.ru'
        }
    )
    url = post_response.json().get('short_url')
    delete_response = requests.delete(url)
    assert delete_response.json().get('short_url') == url
    assert delete_response.json().get('deleted')
    get_response = requests.get(url)
    assert get_response.status_code == HTTPStatus.GONE


def test_status(start_server):
    post_response = requests.post(
        'http://127.0.0.1:8080/api/v1/short_url/',
        json={
            'origin_url': 'http://ya.ru'
        }
    )
    url = post_response.json().get('short_url')
    requests.get(url)
    requests.get(url)
    status_response = requests.get(url + '/status')
    assert status_response.json().get('requests_number') == 2
    status_response_full = requests.get(url + '/status', params={
        'full-info': True
    })
    results = status_response_full.json()
    print('-----------------results', results)
    assert len(results) == 2
    for result in results:
        assert result.get('made_at')
        assert result.get('client_host')
        assert result.get('client_port')
