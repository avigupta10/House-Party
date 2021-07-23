from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from spotify.models import Listeners
from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, SettingsSerializer


class RoomView(ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class GetRoom(APIView):
    serializer_class = RoomSerializer

    def get(self, request):
        code = request.GET.get('code')
        if code:
            room = Room.objects.filter(code=code)
            if room.exists():
                data = RoomSerializer(room[0]).data
                data['is_host'] = request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not found': "Invalid Room Code"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Code Not Found'}, status=status.HTTP_400_BAD_REQUEST)


class JoinRoom(APIView):

    def post(self, request):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        code = request.data.get('code')
        if code:
            obj = Room.objects.filter(code=code)
            if obj.exists():
                room = obj[0]
                self.request.session['room_code'] = room.code
                return Response({'Success': 'Room Joined'}, status=status.HTTP_200_OK)
            return Response({'error': 'Room Not Found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Invalid Code'}, status=status.HTTP_400_BAD_REQUEST)


class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            room, created = Room.objects.update_or_create(host=host, defaults=dict(guest_can_pause=guest_can_pause,
                                                                                   votes_to_skip=votes_to_skip))
            self.request.session['room_code'] = room.code
            return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)


class UserInRoom(APIView):
    def get(self, request):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data = {
            'code': self.request.session.get('room_code'),
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


class DeleteRoom(APIView):
    def post(self, request):
        if 'guest_name' in self.request.session:  # Delete all guest instances
            del self.request.session['guest_name']

        if 'room_code' in self.request.session:
            del self.request.session['room_code']

            host = self.request.session.session_key
            Listeners.objects.filter(user=host).delete()

            res = Room.objects.filter(host=host)

            if res.exists():  # Deleting ROOM if Host
                room = res[0]
                Listeners.objects.filter(room=room).delete()
                room.delete()
        return Response({'Message': 'Room deleted'}, status=status.HTTP_200_OK)


class SettingsView(APIView):
    serializer_class = SettingsSerializer

    def patch(self, request):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            qs = Room.objects.filter(code=code)
            if not qs.exists():
                return Response({'Message': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
            room = qs[0]
            host_id = self.request.session.session_key
            if room.host != host_id:
                return Response({'Message': 'You are not he host'}, status=status.HTTP_403_FORBIDDEN)
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        return Response({'Bad Request': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
