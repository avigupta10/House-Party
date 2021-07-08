import requests
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.models import Room
from .misc import create_update_tokens, CheckAuthentication, get_spotifyAPI_data, update_room_song, get_user_data
from .models import Vote
from .secrets import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI

PLAYLIST_ENDPOINT = "https://api.spotify.com/v1/users/{user_id}/playlists"
PLAY_ENDPOINT = "/player/play"
SKIP_ENDPOINT = "/player/next"
PAUSE_ENDPOINT = "/player/pause"
CURRENT_SONG_ENDPOINT = "/player/currently-playing"
SEARCH_ENDPOINT = "	https://api.spotify.com/v1/search"
USER_ALBUMS_ENDPOINT = "/albums"


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
    error = request.GET.get('error')
    print(error)

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

    song_data = {
        'username': get_user_data(host)['display_name'],
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
