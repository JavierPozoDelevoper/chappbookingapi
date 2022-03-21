from rest_framework import serializers
from api.models import RoomType, Booking
from django.utils import timezone
from django.utils.crypto import get_random_string

class RoomTypeSerializers(serializers.ModelSerializer):
    empty_rooms = serializers.SerializerMethodField()

    class Meta:
        model = RoomType
        fields = '__all__'  
    
    def get_empty_rooms(self, obj):
        return obj.get_empty_rooms(
            start_date=self.context['start_date'],
            end_date=self.context['end_date'])


class BookingSerializers(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ['amount', 'booking_reference', 'room_number']
    
    def create(self, validated_data):
        booking = Booking(**validated_data)
        booking.amount = booking.calculate_amount()
        booking.booking_reference = get_random_string(length=20)
        booking.save()
        return booking

    def update(self, instance, validated_data):
        instance.save()
        return instance

    def validate(self, attrs):
        """
        Validate booking before create or update in DDBB
        """
        self.check_dates(attrs=attrs)
        self.check_guest(attrs=attrs)
        self.check_available_rooms(attrs=attrs)
        return attrs
    
    def check_dates(self , attrs):
        """
        Check not create bookings for days before today
        """
        if attrs['start_date'] < timezone.now().date() :
            raise serializers.ValidationError({"start_date": "Start_date can't be before today"})

        """
        Check that the start is before the end.
        """
        if attrs['start_date'] > attrs['end_date']:
            raise serializers.ValidationError({"end_date": "finish must occur after start"})
        
        """
        Only can booking for current year
        """
        if attrs['end_date'].year != timezone.now().year:
            raise serializers.ValidationError({"end_date": "finish must occur in current year"})
    
    def check_guest(self, attrs):
        """
        Check that guests in booking is less than room type max guest
        """
        if attrs['room_type'].max_guest < attrs['num_guest']:
            raise serializers.ValidationError({"num_guest": "Guests can be more than max room guest"})

    def check_available_rooms(self, attrs):
        """
        Check if have enougth rooms for range of dates
        """
        min_empty_rooms = attrs['room_type'].get_empty_rooms(start_date=attrs['start_date'], end_date=attrs['end_date'])
        if min_empty_rooms <= 0:
            raise serializers.ValidationError({"num_guest": "Not have enougth empty rooms"})

