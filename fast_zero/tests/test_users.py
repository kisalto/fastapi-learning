from http import HTTPStatus

from fast_zero.schemas import UserPublic


# ----------DEFAULT USERS----------
def user_same_name(client, user):
    return client.post(
        '/users/',
        json={
            'username': 'batata',
            'email': 'batata@email.com',
            'password': 'joshua',
        },
    )


def user_same_mail(client, user):
    return client.post(
        '/users/',
        json={
            'username': 'Joshua',
            'email': 'batata@email.com',
            'password': 'senha',
        },
    )


def user_new(client, user):
    return client.post(
        '/users/',
        json={
            'username': 'Joshua',
            'email': 'teste@email.com',
            'password': 'senha',
        },
    )


def user_extra(client, user, token):
    return client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Allan',
            'email': 'teste@email.com',
            'password': 'senha',
        },
    )


# ----------CREATE----------
def test_create_user(client, user):
    response = user_new(client, user)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'username': 'Joshua',
        'email': 'teste@email.com',
        'id': 2,
    }


# ----------READ----------
def test_read(client):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_read_with_users(client, user):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


# ---------UPDATE----------
def test_update(client, user, token):
    response = user_extra(client, user, token)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'username': 'Allan',
        'email': 'teste@email.com',
        'id': user.id,
    }


def test_update_wrong(client, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Allan',
            'email': 'teste@email.com',
            'password': 'senha',
        },
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Permissões insuficientes'}


def test_update_integrity_error(client, user, token):
    user_new(client, user)

    response_update = user_extra(client, user, token)
    assert response_update.status_code == HTTPStatus.CONFLICT

    assert response_update.json() == {'detail': 'Username ou Email ja existe'}


# **********Corrigir*********
# def test_update_err(client):
#     response = client.put(
#         '/users/2', json={'username': '', 'email': '', 'password': ''}
#     )
#     assert response.status_code == HTTPStatus.UNAUTHORIZED


# ----------DELETE----------
def test_del(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_del_wrong(client, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Permissões insuficientes'}


# **********Corrigir*********
# def test_del_err(client):
#     response = client.delete('/users/2')
#     assert response.status_code == HTTPStatus.UNAUTHORIZED


# ----------SOME ERRORS----------
def test_username_err(client, user):
    response = client.post(
        '/',
        json={
            'username': user.username,
            'email': 'batata@email.com',
            'password': 'joshua',
        },
    )

    assert response.json() == {'detail': 'Method Not Allowed'}
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


def test_email_err(client, user):
    response = client.post(
        '/',
        json={
            'username': 'teste',
            'email': user.email,
            'password': 'joshua',
        },
    )

    assert response.json() == {'detail': 'Method Not Allowed'}
    assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED
