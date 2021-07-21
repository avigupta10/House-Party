import time
from datetime import timedelta

import requests
from django.utils import timezone

from .models import Token, Vote
from .secrets import *

BASE_URL = 'https://api.spotify.com/v1'


def get_user_tokens(session_key):
    token = Token.objects.filter(user=session_key)
    if token.exists():
        return token[0]
    else:
        return None


def create_update_tokens(session_key, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_key)
    expires_in = timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token',
                                   'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = Token(user=session_key, access_token=access_token,
                       refresh_token=refresh_token, token_type=token_type, expires_in=expires_in)
        tokens.save()


def CheckAuthentication(session_key):
    tokens = get_user_tokens(session_key)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_key)

        return True

    return False


def refresh_spotify_token(session_key):
    refresh_token = get_user_tokens(session_key).refresh_token
    print('refreshing token')
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')

    create_update_tokens(
        session_key, access_token, token_type, expires_in, refresh_token)


def get_spotifyAPI_data(session_key, ENDPOINT, _put=False, _post=False):
    tokens = get_user_tokens(session_key)
    if tokens:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {tokens.access_token}'}

        if _post:
            requests.post(BASE_URL + ENDPOINT, headers=headers)
        if _put:
            requests.put(BASE_URL + ENDPOINT, headers=headers)

        response = ''
        while response == '':
            try:
                response = requests.get(BASE_URL + ENDPOINT, headers=headers)
                break
            except:  # to handle max request error
                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(5)
                print("Was a nice sleep, now let me continue...")
                continue
        try:
            return response.json()
        except Exception as e:
            return {'error': 'Invalid request or try to play a song ' + str(e)}
    return {'error': 'room doesnt exist'}


def update_room_song(room, song_id):
    current_song = room.current_song

    if current_song != song_id:
        room.current_song = song_id
        room.save(update_fields=['current_song'])
        Vote.objects.filter(room=room).delete()


def get_user_data(host):
    return get_spotifyAPI_data(host, '/me')
