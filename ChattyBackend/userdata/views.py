from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from ChattyBackend import settings
from .models import Users, ResetPasswordToken, AccountVerificationToken, Profile, ResetPasswordSecureToken
from .serializer import UserSerializer, ProfileSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@swagger_auto_schema(
    method='POST',
    operation_description="Sign up a new user and send a verification token via email.",
    request_body=UserSerializer,
    responses={
        201: "User created successfully and verification token sent",
        400: "Bad request with details"
    }
)
@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # Generate a verification token
        verification_token = AccountVerificationToken.objects.create(user=user)

        # Set email subject and context for the template
        subject = 'Account Verification'
        app_name = "Chatty"  # Replace with your app's name
        app_logo_url = "https://example.com/logo.png"  # Replace with the URL to your app's logo
        context = {
            'app_name': app_name,
            'app_logo_url': app_logo_url,
            'token': verification_token.token,
        }

        # Render the HTML template with context
        html_content = render_to_string('verification_email.html', context)
        text_content = strip_tags(html_content)  # Strip HTML tags for plain text version

        # Send the email with both HTML and plain text
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,  # Plain text content
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        return JsonResponse({
            'message': 'User created successfully. Verification token sent to email.',
            'user_id': user.user_id
        }, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description="Verify a user's account using the token.",
    responses={
        200: "Account verified successfully",
        400: "Token expired or invalid",
    },
)
@api_view(['POST'])
def verify_account(request):
    user_id = request.data.get("user_id")
    token = request.data.get("token")

    try:
        user = Users.objects.get(user_id=user_id)
        verification_token = AccountVerificationToken.objects.get(user=user, token=token)

        # Check if the token is expired
        if verification_token.is_expired():
            AccountVerificationToken.objects.filter(user=user, token=token).delete()
            return JsonResponse({"message": "Token expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Mark user as verified
        user.is_verified = True
        user.save()

        # Delete the token after verification
        AccountVerificationToken.objects.filter(user=user, token=token).delete()

        return JsonResponse({"message": "Account verified successfully"}, status=status.HTTP_200_OK)

    except (Users.DoesNotExist, ResetPasswordToken.DoesNotExist):
        return JsonResponse({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


login_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
        'password': openapi.Schema(type=openapi.TYPE_STRING, description='User password'),
    },
    required=['email', 'password']
)


@swagger_auto_schema(
    method='POST',
    operation_description="Login a user after verifying that they are registered and verified.",
    request_body=login_request_schema,
    responses={
        200: openapi.Response(description="User logged in successfully"),
        400: openapi.Response(description="Bad request, invalid credentials or missing fields"),
        404: openapi.Response(description="User not found"),
    }
)
@api_view(['POST'])
def login(request):
    # Extract email and password from request
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return JsonResponse({"message": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve user by email
        user = Users.objects.get(email=email)

        # Check if user is verified and authenticated
        if user.is_verified and user.check_password(password):
            return JsonResponse(
                {"message": "Login permitted", "user_id": user.user_id},
                status=status.HTTP_200_OK
            )
        elif not user.is_verified:
            return JsonResponse({"message": "User is not verified."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"message": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)

    except Users.DoesNotExist:
        return JsonResponse({"message": "No user found with this email."}, status=status.HTTP_404_NOT_FOUND)

'''
Post_profile_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='The user name'),
        'Bio': openapi.Schema(type=openapi.TYPE_STRING, description='The bio that would appear on the profile'),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='The user id'),
        'profile_picture': openapi.Schema(type=openapi.TYPE_STRING, description='The user profile picture'),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='The user phone number'),
    },
    required=['name', 'Bio', 'user_id', 'profile_picture', 'phone_number']
)

Get_profile_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, description='The user name'),
        'Bio': openapi.Schema(type=openapi.TYPE_STRING, description='The bio that would appear on the profile'),
        'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='The user id'),
        'profile_picture': openapi.Schema(type=openapi.TYPE_STRING, description='The user profile picture'),
        'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='The user phone number'),
    },
    required=['user_id']
)


@swagger_auto_schema(
    method='post',
    operation_description="Create a profile using the user_id.",
    request_body=Post_profile_schema,
    responses={
        200: openapi.Response(description="Profile created successfully"),
        400: openapi.Response(description="Bad request, invalid data or missing fields"),
        404: openapi.Response(description="User not found"),
    }
)
@swagger_auto_schema(
    method='get',
    operation_description="Retrieve a profile using the user_id.",
    manual_parameters=[
        openapi.Parameter('user_id', openapi.IN_QUERY, description="The user id", type=openapi.TYPE_STRING)],
    responses={
        200: openapi.Response(description="Profile retrieved successfully"),
        400: openapi.Response(description="Bad request, invalid data or missing fields"),
        404: openapi.Response(description="User not found")
    }
)
@api_view(['GET', 'POST'])
def profile(request):
    user_id = request.GET.get('user_id')
    profile = Profile.objects.get(user__user_id=user_id)
    try:
        if request.method == "GET":
            serializer = ProfileSerializer(profile)
            # Return the serialized data as JSON
            return JsonResponse(serializer.data, safe=False, status=200)

        elif request.method == 'POST':
            serializer = ProfileSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data, safe=False, status=200)
            else:
                return JsonResponse(serializer.errors, status=400)

    except Profile.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)'''


password_reset_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description='The email of the user for password reset request',
        ),
    },
    required=['email'],
)


@swagger_auto_schema(
    method='GET',
    operation_description="Request a password reset token for the user with the given email.",
    request_body=password_reset_request_schema,
    responses={
        201: openapi.Response(
            description="Password reset token sent successfully.",
            examples={
                'application/json': {
                    'message': 'Reset password token sent.',
                    'email': 'user@example.com',
                    'token': 'abc123',
                },
            },
        ),
        404: openapi.Response(
            description="User not found with the given email.",
            examples={
                'application/json': {
                    'error': 'User with this email does not exist',
                },
            },
        ),
    },
)
@api_view(['GET'])
def password_reset_request(request, rqemail):
    try:
        user = Users.objects.get(email=rqemail)
        print(user)
    except Users.DoesNotExist:
        return JsonResponse({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)

    user_tok = ResetPasswordToken.objects.create(user=user)
    print(user_tok)
    user_id = user.user_id
    # Set email subject and context for the template
    subject = 'Password Reset'
    app_name = "Chatty"  # Replace with your app's name
    app_logo_url = "https://example.com/logo.png"  # Replace with the URL to your app's logo
    context = {
        'app_name': app_name,
        'app_logo_url': app_logo_url,
        'token': ResetPasswordToken.token,
    }

    # Render the HTML template with context
    html_content = render_to_string('verification_email.html', context)
    text_content = strip_tags(html_content)  # Strip HTML tags for plain text version

    # Send the email with both HTML and plain text
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # Plain text content
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[rqemail]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()

    return JsonResponse({
        'message': 'Reset password token sent.', 'user_id': user_id},
        status=status.HTTP_201_CREATED)


password_reset_confirm_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'email': openapi.Schema(
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_EMAIL,
            description='The email of the user for password reset',
        ),
        'token': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='The password reset token',
        ),
        'new_password': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='The new password for the user',
        ),
    },
    required=['email', 'token', 'new_password'],
)


@swagger_auto_schema(
    method='POST',
    operation_description="Reset a user's password using the token.",
    request_body=password_reset_confirm_schema,
    responses={
        200: openapi.Response(
            description="Password reset successfully.",
            examples={
                'application/json': {
                    'message': 'Password reset successfully',
                },
            },
        ),
        400: openapi.Response(
            description="Invalid token or missing new password.",
            examples={
                'application/json': {
                    'error': 'Invalid token or missing new password',
                },
            },
        ),
    },
)
@api_view(['POST', 'PATCH'])
def password_reset_confirm(request, user_id):
    token = request.data.get('token')

    if request.method == "POST":
        try:
            user = Users.objects.get(user_id=user_id)  # Get the user instance
            reset_token = ResetPasswordToken.objects.get(token=token)

            if reset_token.is_expired():
                ResetPasswordToken.objects.filter(token=token).delete()
                return JsonResponse({"message": "Token expired"}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new ResetPasswordSecureToken
            ResetPasswordSecureToken.objects.create(user=user)

            # Delete the token after verification
            ResetPasswordToken.objects.filter(token=token).delete()

        except (Users.DoesNotExist, ResetPasswordToken.DoesNotExist):
            return JsonResponse({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({"message": "Token verified"}, status=status.HTTP_201_CREATED)

    if request.method == "PATCH":
        user = Users.objects.get(user_id=user_id)

        new_password = request.data.get('new_password')
        user.set_password(new_password)
        user.save()
        return JsonResponse({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

'''Two step login & resent token '''
