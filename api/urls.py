from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (PropertyViewSet, EquipmentViewSet, BookingViewSet, 
                   FavoriteViewSet, ReviewViewSet, SupportTicketViewSet, 
                   ChatMessageViewSet, register, login, logout,
                   admin_conversations, admin_user_messages, admin_reply, update_profile,
                   owner_status, admin_all_bookings, admin_update_booking,
                   owner_booking_requests, owner_update_booking_request,
                   get_notifications, mark_notifications_read, unread_notification_count,
                   confirm_receipt, return_item, admin_confirm_return, cancel_booking, request_extension, lift_restriction, equipment_booked_dates,
                   forgot_password, verify_reset_code, reset_password, verify_email)

router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'reviews', ReviewViewSet)
router.register(r'support-tickets', SupportTicketViewSet, basename='support-ticket')
router.register(r'chat-messages', ChatMessageViewSet, basename='chat-message')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/profile/', update_profile, name='update-profile'),
    path('owner/is_owner/', owner_status, name='owner-status'),
    path('owner/bookings/', owner_booking_requests, name='owner-booking-requests'),
    path('owner/bookings/<int:booking_id>/', owner_update_booking_request, name='owner-update-booking-request'),
    path('admin/conversations/', admin_conversations, name='admin-conversations'),
    path('admin/conversations/<int:user_id>/messages/', admin_user_messages, name='admin-user-messages'),
    path('admin/conversations/<int:user_id>/reply/', admin_reply, name='admin-reply'),
    path('admin/bookings/', admin_all_bookings, name='admin-all-bookings'),
    path('admin/bookings/<int:booking_id>/', admin_update_booking, name='admin-update-booking'),
    path('notifications/', get_notifications, name='notifications'),
    path('notifications/read/', mark_notifications_read, name='notifications-read'),
    path('notifications/unread-count/', unread_notification_count, name='notifications-unread-count'),
    path('bookings/<int:booking_id>/confirm-receipt/', confirm_receipt, name='confirm-receipt'),
    path('bookings/<int:booking_id>/cancel/', cancel_booking, name='cancel-booking'),
    path('bookings/<int:booking_id>/extension/', request_extension, name='request-extension'),
    path('bookings/<int:booking_id>/return/', return_item, name='return-item'),
    path('admin/bookings/<int:booking_id>/confirm-return/', admin_confirm_return, name='admin-confirm-return'),
    path('admin/users/<int:user_id>/lift-restriction/', lift_restriction, name='lift-restriction'),
    path('equipment/<int:equipment_id>/booked-dates/', equipment_booked_dates, name='equipment-booked-dates'),
    path('auth/forgot-password/', forgot_password, name='forgot-password'),
    path('auth/verify-reset-code/', verify_reset_code, name='verify-reset-code'),
    path('auth/reset-password/', reset_password, name='reset-password'),
    path('auth/verify-email/', verify_email, name='verify-email'),
]
