from pickle import FALSE
from django.db import models
from model_utils.models import SoftDeletableModel
from datetime import timedelta
# Create your models here.

class RoomType(SoftDeletableModel):
    description = models.CharField(max_length=200, null=False)   
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    max_guest = models.IntegerField(default=0)
    available_rooms = models.IntegerField(default=0)  
 
    def get_empty_rooms(self, start_date, end_date):
        """
        Get Empty rooms for a range of dates
        """
        if start_date is None or end_date is None or end_date < start_date:
            return 0

        delta = end_date - start_date
        min_empty_rooms = self.available_rooms
        for dayadd in range(0, delta.days + 1):
            date = start_date + timedelta(days=dayadd)
            bookings = Booking.objects.filter(room_type=self).filter(start_date__gte=date).filter(end_date__lte=date)
            empty_rooms = self.available_rooms - bookings.count()
            if empty_rooms < min_empty_rooms:
                min_empty_rooms = empty_rooms
        
        return min_empty_rooms

    def __str__(self):
	    return self.description

class Booking(models.Model):
    start_date = models.DateField('Start Date booking')
    end_date = models.DateField('End Date booking')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    num_guest = models.IntegerField(default=1)
    contact_name = models.CharField(max_length=200, null=FALSE)
    contact_email = models.CharField(max_length=200, null=FALSE)
    contact_phone = models.CharField(max_length=20, null=FALSE)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    booking_reference = models.CharField(max_length=40, null=True);
    room_number = models.IntegerField(null=True)

    def __str__(self):
        return "Booking from {start_date} to {end_date} with {num_guest} and room type {room_type}.".format(
            start_date = self.start_date,
            end_date = self.end_date,
            num_guest = self.num_guest,
            room_type= self.room_type.description )

    def calculate_amount(self):       
        delta= self.end_date - self.start_date        
        return (delta.days + 1) * self.room_type.amount
