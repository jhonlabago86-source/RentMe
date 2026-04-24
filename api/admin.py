from django.contrib import admin
from .models import UserProfile, Property, Equipment, Booking, Favorite, Review, SupportTicket, ChatMessage

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    exclude = ('owner',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    exclude = ('owner',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

admin.site.register(UserProfile)
admin.site.register(Booking)
admin.site.register(Favorite)
admin.site.register(Review)
admin.site.register(SupportTicket)
admin.site.register(ChatMessage)
