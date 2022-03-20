# Python
import datetime
from datetime import timedelta

# Django
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone,dateformat

# Django Rest Framework
from rest_framework.test import APITestCase
from rest_framework import status

# Models
from api.models import Booking, RoomType

# Definition of methods to create test models
def create_room_type(amount, max_guest, available_rooms):
    roomType = RoomType.objects.create(
        description = "Room type test",
        amount = amount,
        max_guest = max_guest,
        available_rooms =  available_rooms
    ) 
    return roomType

def create_booking(date, days, num_guest, room_type, save = True):
    booking = Booking(
        start_date= date,
        end_date= date + timedelta(days=days-1),
        num_guest=num_guest,
        contact_name = 'test name',
        contact_email= "test@gmail.com",
        contact_phone = "666666666",            
        booking_reference= "123456789",
        room_number= 23,
        room_type= room_type
    )
    if(save):
        booking.save()

    booking.amount = booking.calculate_amount()
    return booking

# Create your tests here.
class BookingModelTestCase(TestCase):
    def test_calculate_amount(self):
        """
        Check calculate amount price of booking. 2 days for 20€ = 40€
        """        
        roomType = create_room_type(amount=20, max_guest=1, available_rooms=10)
        booking= create_booking(date=timezone.now(), days=2, num_guest=1, room_type=roomType)
        self.assertIs(booking.amount, 40)
        
        booking= create_booking(date=timezone.now(), days=1, num_guest=1, room_type=roomType)
        self.assertIs(booking.amount, 20)


class BookingAPITestCase(APITestCase):
    def test_get_bookings(self):
        """
        Check if Bookings index works and return object in json.
        """
        #Arrange Booking Data        
        roomType = create_room_type(20, 1, 10)
        create_booking(date=timezone.now(), days=1, num_guest=1, room_type=roomType)

        #Act
        url = reverse('api:booking')
        response = self.client.get(url, format='json')
        
        #Assert Status and len = 1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_no_get_past_bookings(self):
        """
        No return bookings with end date is after today
        """
         #Arrange Booking Data   
        roomType = create_room_type(20, 1, 10)
        create_booking(date=timezone.now(), days=1, num_guest=1, room_type=roomType)
        create_booking(date=timezone.now()+ timedelta(days=-10), days=1, num_guest=1, room_type=roomType)            

        #Act
        url = reverse('api:booking')
        response = self.client.get(url, format='json')
        
        #Assert Status and len = 1
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_booking(self):
        """
        Ensure we can create a new booking.
        """
        create_room_type(amount=20, max_guest=1, available_rooms=2)         
        data = {
            'start_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'end_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'room_type': 1,
            'num_guest': 1,
            'contact_name': 'test',
            'contact_email': 'test@email',
            'contact_phone': '666666666'
        }

        url = reverse('api:booking')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)  
    
    def test_no_create_end_date_before_booking(self):
        """
        Not save booking if end date is before to start date
        """
        create_room_type(amount=20, max_guest=1, available_rooms=2)               
        data = {
            'start_date': dateformat.format(timezone.now() + timedelta(days=3) , 'Y-m-d'),
            'end_date': dateformat.format(timezone.now() + timedelta(days=2), 'Y-m-d'),
            'room_type': 1,
            'num_guest': 1,
            'contact_name': 'test',
            'contact_email': 'test@email',
            'contact_phone': '666666666'
        }
        
        url = reverse('api:booking')
        response = self.client.post(url, data, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 0)       

    def test_create_only_this_year_booking(self):
        """
        Not save booking if end date is before to start date
        """
        create_room_type(amount=20, max_guest=1, available_rooms=2)    
        end_date = datetime.datetime(day=1, month=1, year=timezone.now().date().year + 1)
        data = {
            'start_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'end_date': dateformat.format(end_date, 'Y-m-d'),
            'room_type': 1,
            'num_guest': 1,
            'contact_name': 'test',
            'contact_email': 'test@email',
            'contact_phone': '666666666'
        }
        
        url = reverse('api:booking')
        response = self.client.post(url, data, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 0)

    def test_not_create_when_guest_booking_greather_than_room_type(self):
        """
        Not save booking if num_guest is greather than guest of room type
        """
        create_room_type(amount=20, max_guest=1, available_rooms=2)       
        data = {
            'start_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'end_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'room_type': 1,
            'num_guest': 2,
            'contact_name': 'test',
            'contact_email': 'test@email',
            'contact_phone': '666666666'
        }
        
        url = reverse('api:booking')
        response = self.client.post(url, data, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 0)    
        
    def test_not_create_when_not_enougth_room_available_one_day(self):
        """
        Test for not create booking if an day not have enougth available room for one day.
        """
        roomType = create_room_type(amount=20, max_guest=2, available_rooms=2)   
        create_booking(date=timezone.now(), days=1, num_guest=1, room_type=roomType)
        create_booking(date=timezone.now(), days=1, num_guest=1, room_type=roomType)
        data = {
            'start_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'end_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'room_type': 1,
            'num_guest': 1,
            'contact_name': 'test',
            'contact_email': 'test@email',
            'contact_phone': '666666666'
        }
        url = reverse('api:booking')
        response = self.client.post(url, data, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)   

    def test_not_create_when_not_enougth_room_available_some_days(self):
        """
        Test for not create booking if an day not have enougth available room for some days.
        """
        roomType = create_room_type(amount=20, max_guest=2, available_rooms=2)           
        create_booking(date=timezone.now()+ timedelta(days=1), days=1, num_guest=2, room_type=roomType)
        create_booking(date=timezone.now()+ timedelta(days=1), days=1, num_guest=2, room_type=roomType)
        data = {
            'start_date': dateformat.format(timezone.now(), 'Y-m-d'),
            'end_date': dateformat.format(timezone.now() + timedelta(days=1), 'Y-m-d'),
            'room_type': 1,
            'num_guest': 1,
            'contact_name': 'test',
            'contact_email': 'test@email',
            'contact_phone': '666666666'
        }
        url = reverse('api:booking')
        response = self.client.post(url, data, format='json')

        self.assertNotEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 2)       