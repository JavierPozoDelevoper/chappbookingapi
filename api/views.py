from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RoomTypeSerializers, BookingSerializers
from .models import RoomType, Booking
from rest_framework import status
from django.utils import timezone
from datetime import datetime
from django.utils.timezone import make_aware

# Create your views here.
class RoomType_APIView(APIView):
    def get(self, request, format=None, *args, **kwargs):
        num_guest = self.request.query_params.get('num_guest')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        roomTypes = RoomType.objects.all()
        """
        Filter of num_guest
        """
        if num_guest is not None:
            roomTypes = roomTypes.filter(max_guest__gte=num_guest)                

        if start_date is not None and end_date is not None:            
            start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))            

        serializer = RoomTypeSerializers(
            roomTypes,
            many=True,
            context={'start_date': start_date, 'end_date':end_date})              
        return Response(serializer.data)


class Booking_APIView(APIView):   
    def get(self, request, format=None, *args, **kwargs):
        bookings = Booking.objects.filter(
            end_date__gte=timezone.now()
        ).order_by('end_date')
        serializer = BookingSerializers(bookings, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = BookingSerializers(data=request.data)
        if serializer.is_valid():            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)