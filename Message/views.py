from rest_framework.decorators import api_view
from .models import Message
from .serializers import MessageSerializer
from rest_framework.response import Response

@api_view(['GET'])
def get_messages(request):
    sender = request.GET.get('sender')
    receiver = request.GET.get('receiver')
    messages = Message.objects.filter(sender=sender, receiver=receiver) | Message.objects.filter(sender=receiver, receiver=sender)
    messages = messages.order_by('timestamp')
    return Response(MessageSerializer(messages, many=True).data)

@api_view(['POST'])
def send_message(request):
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

