from http import HTTPStatus

from freezegun import freeze_time


# ----------TOKEN----------
def test_get_token(client, user):
    response = client.post(
        'auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_expire(client, user):
    with freeze_time('2026-04-07 14:00'):
        response = client.post(
            'auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2026-04-07 14:31'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'errado',
                'email': 'errado@email.com',
                'password': 'errado',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Não foi possivel validar o token'
        }


def test_token_inexistente(client, user):
    response = client.post(
        'auth/token',
        data={'username': 'no_user@no_domain.com', 'password': 'testeteste'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Email ou senha incorreta'}


def test_wrong_password(client, user):
    response = client.post(
        'auth/token', data={'username': user.email, 'password': 'senha errada'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Email ou senha incorretos'}


def test_refresh_token(client, token):
    response = client.post(
        'auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_refresh_expirado(client, user, token):
    with freeze_time('2026-04-07 16:00:00'):
        response = client.post(
            'auth/token',
            data={
                'username': user.email,
                'password': user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert response.json()['access_token']

    with freeze_time('2026-04-07 16:50:00'):
        response = client.post(
            'auth/refresh_token', headers={'Authorization': f'Bearer {token}'}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {
            'detail': 'Não foi possivel validar o token'
        }
