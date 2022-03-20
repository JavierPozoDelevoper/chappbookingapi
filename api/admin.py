from django.contrib import admin
from .models import RoomType, Booking

# Register your models here.
class BookingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['start_date','end_date','room_type','num_guest']}),
        ('Contact Data', {'fields': ['contact_name','contact_email','contact_phone']}),
        ('Room Data', {'fields': ['booking_reference', 'room_number']}),
        ('Pricing', {'fields': ['amount']})        
    ]
    list_display = ('start_date', 'end_date', 'room_type', 'num_guest', 'amount', 'contact_name','booking_reference')
    list_filter = ['start_date','end_date']
    search_fields = ['booking_reference']

class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ('description', 'available_rooms', 'amount')
    search_fields = ['description']

admin.site.register(Booking, BookingAdmin)
admin.site.register(RoomType, RoomTypeAdmin)