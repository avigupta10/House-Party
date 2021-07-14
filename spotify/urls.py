from django.urls import path
from spotify import views

app_name = 'frontend'

urlpatterns = [
    path('get-auth-url', views.get_auth_url, name='get_auth_url'),
    path('redirect', views.spotify_callback, name='redirect'),
    path('is-authenticated', views.IsAuthenticated, name='is_authenticated'),
    path('current-song', views.CurrentSong, name='current-song'),
    path('play-song', views.PlaySong, name='play-song'),
    path('pause-song', views.PauseSong, name='pause-song'),
    path('skip-song', views.SkipSong, name='skip-song'),
    path('search-song', views.SearchSong, name='search-song'),
    path('play-search', views.Play, name='play-search'),
]
