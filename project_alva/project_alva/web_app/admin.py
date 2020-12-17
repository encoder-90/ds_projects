from django.contrib import admin
from .models import CustomUser, History, Subscription, ApartmentType, ConstructionType, District, ContactMessage

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(History)
admin.site.register(Subscription)
admin.site.register(ApartmentType)
admin.site.register(ConstructionType)
admin.site.register(District)
admin.site.register(ContactMessage)
