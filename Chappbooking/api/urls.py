from django.urls import path
from .views import *

app_name = 'api'
urlpatterns = [
    # Room Type URLs
    path('v1/room-type', RoomType_APIView.as_view(), name="room_type"), 

    # Bookings URLs
    path('v1/booking', Booking_APIView.as_view(), name="booking")     
]