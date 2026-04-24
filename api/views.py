from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly, SAFE_METHODS, BasePermission
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from .models import UserProfile, Property, Equipment, Booking, Favorite, Review, SupportTicket, ChatMessage, Notification
from .serializers import (UserSerializer, UserProfileSerializer, RegisterSerializer, 
                         PropertySerializer, EquipmentSerializer, BookingSerializer,
                         FavoriteSerializer, ReviewSerializer, SupportTicketSerializer, ChatMessageSerializer, NotificationSerializer)

class IsAdminOrOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user and request.user.is_staff:
            return True
        return getattr(obj, 'owner', None) == request.user

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user': UserSerializer(user).data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        user_data['is_staff'] = user.is_staff
        return Response({'token': token.key, 'user': user_data})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response({'message': 'Logged out successfully'})

class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = self.queryset
        location = request.query_params.get('location', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        property_type = request.query_params.get('property_type', None)
        
        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_listings(self, request):
        queryset = self.queryset.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminOrOwnerOrReadOnly]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category', None)
        if category:
            queryset = self.queryset.filter(category=category)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response({'error': 'Category parameter required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_listings(self, request):
        queryset = self.queryset.filter(owner=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        from datetime import date, timedelta
        user = self.request.user
        profile, _ = UserProfile.objects.get_or_create(user=user)

        # Auto-restrict if user has bookings overdue by 2+ days
        overdue_bookings = Booking.objects.filter(
            user=user,
            status__in=['confirmed', 'completed'],
            end_date__lt=date.today() - timedelta(days=2)
        )
        if overdue_bookings.exists() and not profile.is_restricted:
            profile.is_restricted = True
            profile.save()
            Notification.objects.create(
                user=user,
                title='🚫 Account Restricted',
                message='Your account has been restricted due to an overdue rental (2+ days). Please return the item and visit our store to resolve this.'
            )

        if profile.is_restricted:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'detail': 'Your account is restricted due to an overdue rental. Please return the item and visit our store to resolve this.'})

        equipment = serializer.validated_data.get('equipment')
        quantity = serializer.validated_data.get('quantity', 1)
        if equipment:
            if not equipment.available:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'equipment': 'This equipment is currently unavailable.'})
            if equipment.quantity < quantity:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'quantity': f'Only {equipment.quantity} unit(s) available.'})
        serializer.save(user=self.request.user, status='requested')

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        equipment_id = self.request.data.get('equipment')
        if equipment_id:
            already = Review.objects.filter(user=self.request.user, equipment_id=equipment_id).exists()
            if already:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({'detail': 'You have already reviewed this equipment.'})
        serializer.save(user=self.request.user)

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_booking_requests(request):
    bookings = Booking.objects.filter(
        Q(property__owner=request.user) | Q(equipment__owner=request.user)
    ).order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def owner_update_booking_request(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    is_property_owner = booking.property and booking.property.owner == request.user
    is_equipment_owner = booking.equipment and booking.equipment.owner == request.user
    if not (is_property_owner or is_equipment_owner):
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

    new_status = request.data.get('status')
    if new_status not in ['confirmed', 'rejected', 'cancelled']:
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

    old_status = booking.status
    if booking.equipment:
        equipment = booking.equipment
        booked_qty = booking.quantity

        if new_status == 'confirmed' and old_status != 'confirmed':
            if equipment.quantity < booked_qty:
                return Response({'error': f'Not enough stock. Only {equipment.quantity} available.'}, status=status.HTTP_400_BAD_REQUEST)
            equipment.quantity -= booked_qty
            equipment.available = equipment.quantity > 0
            equipment.save()
        elif old_status == 'confirmed' and new_status in ['cancelled', 'rejected']:
            equipment.quantity += booked_qty
            equipment.available = True
            equipment.save()

    booking.status = new_status
    booking.admin_note = request.data.get('admin_note', booking.admin_note)
    booking.save()
    return Response(BookingSerializer(booking).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_status(request):
    owns_property = Property.objects.filter(owner=request.user).exists()
    owns_equipment = Equipment.objects.filter(owner=request.user).exists()
    return Response({'is_owner': owns_property or owns_equipment})

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    if request.method == 'GET':
        profile, _ = UserProfile.objects.get_or_create(user=user)
        data = UserSerializer(user).data
        data['phone'] = profile.phone
        data['avatar'] = request.build_absolute_uri(profile.avatar.url) if profile.avatar else None
        data['is_restricted'] = profile.is_restricted
        return Response(data)
    
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    email = request.data.get('email')
    password = request.data.get('password')
    phone = request.data.get('phone')
    avatar = request.FILES.get('avatar')

    if first_name is not None: user.first_name = first_name
    if last_name is not None: user.last_name = last_name
    if email is not None: user.email = email
    if password: user.set_password(password)
    user.save()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    if phone is not None: profile.phone = phone
    if avatar: profile.avatar = avatar
    profile.save()

    data = UserSerializer(user).data
    data['phone'] = profile.phone
    data['avatar'] = request.build_absolute_uri(profile.avatar.url) if profile.avatar else None
    data['is_restricted'] = profile.is_restricted
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lift_restriction(request, user_id):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    try:
        target_user = User.objects.get(id=user_id)
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.is_restricted = False
        profile.save()
        Notification.objects.create(
            user=target_user,
            title='✅ Account Restriction Lifted',
            message='Your account restriction has been lifted. You can now make bookings again. Thank you!'
        )
        return Response({'status': 'restriction lifted'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_bookings(request):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    bookings = Booking.objects.all().order_by('-created_at')
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def admin_update_booking(request, booking_id):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status', booking.status)
    old_status = booking.status

    if booking.equipment:
        equipment = booking.equipment
        booked_qty = booking.quantity

        if new_status == 'confirmed' and old_status != 'confirmed':
            if equipment.quantity < booked_qty:
                return Response({'error': f'Not enough stock. Only {equipment.quantity} available.'}, status=status.HTTP_400_BAD_REQUEST)
            equipment.quantity -= booked_qty
            equipment.available = equipment.quantity > 0
            equipment.save()

        elif old_status == 'confirmed' and new_status in ['cancelled', 'completed']:
            equipment.quantity += booked_qty
            equipment.available = True
            equipment.save()

    booking.status = new_status
    booking.admin_note = request.data.get('admin_note', booking.admin_note)
    booking.save()

    # Auto-send chat message to user on confirmation
    if new_status == 'confirmed' and old_status != 'confirmed':
        item_name = booking.equipment.name if booking.equipment else (booking.property.title if booking.property else 'item')
        pickup_location = request.data.get('pickup_location', '').strip()
        pickup_time = request.data.get('pickup_time', '').strip()
        if booking.delivery_option == 'pickup' and pickup_location and pickup_time:
            message = (
                f"✅ Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) has been confirmed!\n\n"
                f"📍 Pickup Location: {pickup_location}\n"
                f"🕐 Pickup Time: {pickup_time}\n\n"
                f"Please be on time. Thank you for choosing RentMe!"
            )
        else:
            message = (
                f"✅ Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) has been confirmed!\n\n"
                f"{booking.admin_note or 'Thank you for choosing RentMe!'}"
            )
        ChatMessage.objects.create(user=booking.user, message=message, is_support=True)

    # Send notification to user on any status change
    if new_status != old_status:
        item_name = booking.equipment.name if booking.equipment else (booking.property.title if booking.property else 'item')
        pickup_location = request.data.get('pickup_location', '').strip()
        pickup_time = request.data.get('pickup_time', '').strip()

        if new_status == 'confirmed':
            if booking.delivery_option == 'pickup' and pickup_location and pickup_time:
                notif_message = (
                    f"Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) has been confirmed!\n\n"
                    f"📍 Pickup Location: {pickup_location}\n"
                    f"🕐 Pickup Time: {pickup_time}\n\n"
                    f"Please be on time. Thank you for choosing RentMe!"
                )
            else:
                notif_message = (
                    f"Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) has been confirmed!\n"
                    f"{booking.admin_note or 'Thank you for choosing RentMe!'}"
                )
            title = '✅ Booking Confirmed'
        elif new_status == 'cancelled':
            title = '❌ Booking Cancelled'
            notif_message = f"Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) has been cancelled. {booking.admin_note or ''}"
        elif new_status == 'completed':
            title = '🎉 Booking Completed'
            notif_message = f"Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) has been marked as completed. Thank you!"
        else:
            title = '📋 Booking Updated'
            notif_message = f"Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) status changed to {new_status}."

        Notification.objects.create(user=booking.user, title=title, message=notif_message)

    return Response(BookingSerializer(booking).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def return_item(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status != 'completed':
        return Response({'error': 'Only completed bookings can be returned.'}, status=status.HTTP_400_BAD_REQUEST)

    is_damaged = request.data.get('is_damaged', False)
    damage_description = request.data.get('damage_description', '').strip()

    if is_damaged and not damage_description:
        return Response({'error': 'Please describe the damage.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = 'returned_damaged' if is_damaged else 'returning'
    booking.damage_description = damage_description
    booking.save()

    item_name = booking.equipment.name if booking.equipment else (booking.property.title if booking.property else 'item')

    # Notify admin via notification to all staff
    from django.contrib.auth.models import User as AuthUser
    admins = AuthUser.objects.filter(is_staff=True)
    for admin in admins:
        if is_damaged:
            Notification.objects.create(
                user=admin,
                title='⚠️ Item Returned with Damage',
                message=f"'{item_name}' (BK{str(booking.id).zfill(6)}) was returned with damage.\n\nDamage report: {damage_description}"
            )
        else:
            Notification.objects.create(
                user=admin,
                title='📦 Item Being Returned',
                message=f"'{item_name}' (BK{str(booking.id).zfill(6)}) is being returned by {booking.user.username}."
            )

    return Response(BookingSerializer(booking).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_confirm_return(request, booking_id):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status not in ['returning', 'returned_damaged']:
        return Response({'error': 'Booking is not in a returnable state.'}, status=status.HTTP_400_BAD_REQUEST)

    admin_note = request.data.get('admin_note', '').strip()
    is_damaged = booking.status == 'returned_damaged'

    booking.status = 'returned'
    booking.admin_note = admin_note
    booking.save()

    if booking.equipment:
        booking.equipment.quantity += booking.quantity
        booking.equipment.available = True
        booking.equipment.save()

    item_name = booking.equipment.name if booking.equipment else (booking.property.title if booking.property else 'item')

    if is_damaged:
        notif_message = (
            f"Your return of '{item_name}' (BK{str(booking.id).zfill(6)}) has been received.\n\n"
            f"⚠️ Damage was reported. Please visit our store in person to discuss the damage cost.\n"
            f"{admin_note}"
        )
        title = '⚠️ Please Visit Our Store'
        ChatMessage.objects.create(
            user=booking.user,
            message=(
                f"⚠️ Regarding your return of '{item_name}' (BK{str(booking.id).zfill(6)}), "
                f"damage was reported on the item. Please visit our store in person so we can discuss the damage cost. Thank you!"
            ),
            is_support=True
        )
    else:
        notif_message = f"Your return of '{item_name}' (BK{str(booking.id).zfill(6)}) has been confirmed. Thank you!"
        title = '✅ Return Confirmed'

    Notification.objects.create(user=booking.user, title=title, message=notif_message)

    return Response(BookingSerializer(booking).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def equipment_booked_dates(request, equipment_id):
    from datetime import timedelta
    bookings = Booking.objects.filter(
        equipment_id=equipment_id,
        status__in=['requested', 'pending', 'confirmed', 'completed']
    )
    booked_dates = []
    for booking in bookings:
        current = booking.start_date
        while current <= booking.end_date:
            booked_dates.append(str(current))
            current += timedelta(days=1)
    return Response({'booked_dates': list(set(booked_dates))})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_extension(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    reason = request.data.get('reason', '').strip()
    if not reason:
        return Response({'error': 'Please provide a reason.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.extension_reason = reason
    booking.save()

    item_name = booking.equipment.name if booking.equipment else 'item'
    from django.contrib.auth.models import User as AuthUser
    admins = AuthUser.objects.filter(is_staff=True)
    for admin in admins:
        Notification.objects.create(
            user=admin,
            title='⏰ Return Extension Request',
            message=f"{booking.user.username} cannot return '{item_name}' (BK{str(booking.id).zfill(6)}) today.\n\nReason: {reason}"
        )

    return Response(BookingSerializer(booking).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status not in ['requested', 'pending']:
        return Response({'error': 'Only requested or pending bookings can be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = 'cancelled'
    booking.save()

    item_name = booking.equipment.name if booking.equipment else (booking.property.title if booking.property else 'item')
    Notification.objects.create(
        user=booking.user,
        title='❌ Booking Cancelled',
        message=f"Your booking for '{item_name}' (BK{str(booking.id).zfill(6)}) has been cancelled."
    )

    return Response(BookingSerializer(booking).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_receipt(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if booking.status != 'confirmed':
        return Response({'error': 'Only confirmed bookings can be marked as received.'}, status=status.HTTP_400_BAD_REQUEST)

    booking.status = 'completed'
    booking.save()

    item_name = booking.equipment.name if booking.equipment else (booking.property.title if booking.property else 'item')
    Notification.objects.create(
        user=booking.user,
        title='📦 Item Received',
        message=f"You have confirmed receipt of '{item_name}' (BK{str(booking.id).zfill(6)}). Enjoy your rental!"
    )

    return Response(BookingSerializer(booking).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_notification_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'count': count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_conversations(request):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    users = User.objects.filter(chatmessage__isnull=False).distinct()
    result = []
    for user in users:
        last_msg = ChatMessage.objects.filter(user=user).order_by('-created_at').first()
        result.append({
            'user_id': user.id,
            'username': user.username,
            'full_name': f'{user.first_name} {user.last_name}'.strip() or user.username,
            'last_message': last_msg.message if last_msg else '',
            'last_time': last_msg.created_at if last_msg else None,
        })
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_user_messages(request, user_id):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    messages = ChatMessage.objects.filter(user_id=user_id).order_by('created_at')
    serializer = ChatMessageSerializer(messages, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_reply(request, user_id):
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    target_user = User.objects.get(id=user_id)
    msg = ChatMessage.objects.create(
        user=target_user,
        message=request.data.get('message', ''),
        is_support=True
    )
    serializer = ChatMessageSerializer(msg)
    return Response(serializer.data, status=status.HTTP_201_CREATED)
