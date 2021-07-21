import requests
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json

from backend.models import Room
from .misc import create_update_tokens, CheckAuthentication, get_spotifyAPI_data, update_room_song, get_user_data, \
    get_user_tokens
from .models import Vote
from .secrets import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

PLAYLIST_ENDPOINT = "/users/{user_id}/playlists"
PLAY_ENDPOINT = "/me/player/play"
SKIP_ENDPOINT = "/me/player/next"
PAUSE_ENDPOINT = "/me/player/pause"
CURRENT_SONG_ENDPOINT = "/me/player/currently-playing"
SEARCH_ENDPOINT = "/search"
USER_ALBUMS_ENDPOINT = "/me/albums"
QUEUE_ENDPOINT = '/me/player/queue'


@api_view(['GET'])
def get_auth_url(request):
    scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-email'
    url = requests.Request('GET', 'https://accounts.spotify.com/authorize', params={
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'show_dialog': 'true',
        'scope': scopes,
        'redirect_uri': REDIRECT_URI
    }).prepare().url

    return Response({'url': url}, status=status.HTTP_200_OK)


def spotify_callback(request):
    code = request.GET.get('code')
    if 'error' in request.GET:
        raise PermissionDenied

    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': 'true',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')
    print(error)

    if not request.session.exists(request.session.session_key):
        request.session.create()

    create_update_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:index')


@api_view(['GET'])
def IsAuthenticated(request):
    is_authenticated = CheckAuthentication(request.session.session_key)
    return Response({'status': is_authenticated}, status=status.HTTP_200_OK)


@api_view(['GET'])
def CurrentSong(request):
    room_code = request.session.get('room_code')
    room = Room.objects.filter(code=room_code)
    if room.exists():
        room = room[0]
    else:
        return Response({'error': 'Not in a room'}, status=status.HTTP_404_NOT_FOUND)
    host = room.host
    response = get_spotifyAPI_data(host, CURRENT_SONG_ENDPOINT)

    if 'error' in response or 'item' not in response:
        return Response({'error': response['error']}, status=status.HTTP_204_NO_CONTENT)

    item = response.get('item')
    duration = item.get('duration_ms')
    progress = response.get('progress_ms')
    album_cover = item.get('album').get('images')[0].get('url')
    is_playing = response.get('is_playing')
    song_id = item.get('id')

    artists_string = ''

    for i, artist in enumerate(item['artists']):  # if we had multiple artist
        if i > 0:
            artists_string += ', '
        name = artist['name']
        artists_string += name

    votes = len(Vote.objects.filter(room=room, song_id=song_id))

    if request.session.session_key == room.host:
        _username = get_user_data(host)['display_name']
    else:
        _username = 'Guest'
    try:
        song_data = {
            'username': _username,
            'guest_name': 'Guest',
            'title': item['name'],
            'artist': artists_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': votes,
            'votes_required': room.votes_to_skip,
            'id': song_id
        }
    except Exception as e:
        song_data = {
            'username': 'Host name',
            'guest_name': request.session.get('guest_name'),
            'title': 'Song title',
            'artist': 'artists_string',
            'duration': '1000',
            'time': '1000',
            'image_url': 'album_cover',
            'is_playing': False,
            'votes': 'votes',
            'votes_required': 'votes_to_skip',
            'id': 'song_id'
        }

    update_room_song(room=room, song_id=song_id)

    return Response(song_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def PauseSong(request):
    room_code = request.session['room_code']
    room = Room.objects.filter(code=room_code)[0]
    if request.session.session_key == room.host or room.guest_can_pause:
        get_spotifyAPI_data(room.host, PAUSE_ENDPOINT, _put=True)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    return Response({}, status=status.HTTP_403_FORBIDDEN)


@api_view(['PUT'])
def PlaySong(request):
    room_code = request.session['room_code']
    room = Room.objects.filter(code=room_code)[0]
    if request.session.session_key == room.host or room.guest_can_pause:
        get_spotifyAPI_data(room.host, PLAY_ENDPOINT, _put=True)
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    return Response({}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def SkipSong(request):
    room_code = request.session.get('room_code')
    room = Room.objects.filter(code=room_code)[0]
    votes = Vote.objects.filter(room=room, song_id=room.current_song)
    votes_needed = room.votes_to_skip

    if request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
        votes.delete()
        get_spotifyAPI_data(room.host, SKIP_ENDPOINT, _post=True)
    else:
        vote = Vote(user=request.session.session_key, room=room, song_id=room.current_song)
        vote.save()

    return Response({}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def SearchSong(request):
    room_code = request.session.get('room_code')
    room = Room.objects.filter(code=room_code)
    if room.exists():
        room = room[0]
        q = request.GET.get('query')
        print(SEARCH_ENDPOINT + f'?q={q}&type=track')
        response = get_spotifyAPI_data(room.host, SEARCH_ENDPOINT + f'?q={q}&type=track')

        track_names = \
            [
                {
                    "name": response['tracks']['items'][i]['name'],
                    "uri": response['tracks']['items'][i]['uri']
                }
                for i in range(10)
            ]
        return Response(track_names, status=status.HTTP_200_OK)

    return Response({'error': 'not in room'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', "POST"])
def Play(request):
    uris = request.data.get('uris')
    session_key = request.session.session_key
    tokens = get_user_tokens(session_key)
    if tokens:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {tokens.access_token}'}
        payload = {"uris": [uris]}
        resp = requests.put('https://api.spotify.com/v1/me/player/play', headers=headers, data=json.dumps(payload))
        print(resp.json())
        return Response(resp.json(), status=status.HTTP_204_NO_CONTENT)
    return Response({}, status=status.HTTP_403_FORBIDDEN)


@api_view(["POST"])
def set_guest_name(request):
    name = request.data.get('name')
    if request.session.session_key:
        request.session['guest_name'] = name
        return Response({'success':name}, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({'error': 'No Session'}, status=status.HTTP_418_IM_A_TEAPOT)