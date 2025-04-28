from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from chatbot_app.models import ChatMessage
from api.serializers import ChatMessageSerializer


class ActiveChatsView(APIView):

    def get(self, request):
        try:
            all_chats = ActiveChatsView.objects.all()
            print("all_chats", all_chats)
            serializer_data = ChatMessageSerializer(all_chats, many=True).data

            return Response(serializer_data, status=status.HTTP_200_OK)
        
        except:
            return Response({'Error': 'Some error occurs'}, status=status.HTTP_404_NOT_FOUND)