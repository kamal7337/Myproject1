from django.core.cache import cache
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from .permissions import RoleBasedAccessPermission
from django.core.mail import send_mail
from django.conf import settings
from .utils import send_websocket_notification
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

@swagger_auto_schema(method='post', request_body=UserSerializer)
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([RoleBasedAccessPermission])
def user_list(request):
    try:
        if request.method == 'GET':
            cached_users = cache.get('user_list_cache')
            if cached_users:
                return Response(cached_users)
            users = User.objects.all()
            serializer = UserSerializer(users, many=True)
            cache.set('user_list_cache', serializer.data, timeout=60)
            return Response(serializer.data)

        elif request.method == 'POST':
            if not request.user or not request.user.is_authenticated:
                return Response(
                    {"detail": "Authentication credentials were not provided."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()

                
                user_email = serializer.data.get('email')
                user_name = serializer.data.get('name')

                subject = "Welcome to the Community!"
                message = f"Hi {user_name},\n\nYour account has been successfully created.\n\nRegards,\nKamalakar"
                from_email = settings.DEFAULT_FROM_EMAIL
                recipient_list = [user_email]

                try:
                    send_mail(subject, message, from_email, recipient_list)
                except Exception as e:
                    print(f"Error sending email: {e}")

                
                send_websocket_notification(user, f"Hello {user_name}, your account has been created!")

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response({
                "status": "error",
                "message": "Invalid data provided.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            "status": "error",
            "message": "An unexpected error occurred.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(method='put', request_body=UserSerializer)
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([RoleBasedAccessPermission])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": f"User with ID {pk} not found."
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PUT':
        # For updating the user, send a confirmation email
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()

            # Send email notification for user update
            user_email = serializer.data.get('email')
            user_name = serializer.data.get('name')

            subject = "Your Account Information Was Updated"
            message = f"Hi {user_name},\n\nYour account information has been successfully updated.\n\nRegards,\nKamalakar"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user_email]

            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                print(f"Error sending email: {e}")

            
            send_websocket_notification(user, f"Hello {user_name}, your account information has been updated!")

            return Response(serializer.data)

        return Response({
            "status": "error",
            "message": "Invalid update data.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Before deleting the user, send a confirmation email
        user_name = user.name
        user_email = user.email

        user.delete()

        # Send email notification for user deletion
        subject = "Your Account Was Deleted"
        message = f"Hi {user_name},\n\nWe regret to inform you that your account has been deleted.\n\nRegards,\nKamalakar"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user_email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(f"Error sending email: {e}")

        #  Send real-time WebSocket notification for the deletion
        send_websocket_notification(user, f"Hello {user_name}, your account has been deleted.")

        return Response({
            "status": "success",
            "message": f"User {pk} deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)