from django.urls import path
from backend.views import RoomView, CreateRoomView, GetRoom, JoinRoom, UserInRoom, DeleteRoom, SettingsView

urlpatterns = [
    path('room', RoomView.as_view()),
    path('create-room', CreateRoomView.as_view()),
    path('get-room', GetRoom.as_view()),
    path('join-room', JoinRoom.as_view()),
    path('user-in-room', UserInRoom.as_view()),
    path('leave-room', DeleteRoom.as_view()),
    path('settings-room', SettingsView.as_view()),
]
