from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from Chatty_Back import settings
from .models import Users, ResetPasswordToken, AccountVerificationToken
from .serializer import UserSerializer
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
        app_name = "YourAppName"  # Replace with your app's name
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
            return JsonResponse({"message": "Token expired"}, status=status.HTTP_400_BAD_REQUEST)

        # Mark user as verified
        user.is_verified = True
        user.save()

        # Delete the token after verification
        AccountVerificationToken.objects.filter(user=user, token=token).delete()

        return JsonResponse({"message": "Account verified successfully"}, status=status.HTTP_200_OK)

    except (Users.DoesNotExist, ResetPasswordToken.DoesNotExist):
        return JsonResponse({"message": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='POST',
    operation_description="Login a user after verifying that they are registered and verified.",
    request_body=UserSerializer,
    responses={
        200: "User logged in successfully",
        404: "User not found or not verified",
    }
)
@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = Users.objects.get(email=email)

        # Ensure user is verified and password is correct
        if user.check_password(password) and user.is_verified:
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)

        # Check if user exists but isn't verified
        elif not user.is_verified:
            return JsonResponse({'error': 'User account is not verified'}, status=status.HTTP_403_FORBIDDEN)

    except Users.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='GET',
    operation_description="Retrieve users from the Database.",
    responses={200: UserSerializer(many=True)}
)
@api_view(['GET'])
def user_list_create(request):
    if request.method == 'GET':
        users = Users.objects.all()
        serializer = UserSerializer(users, many=True)
        return JsonResponse(serializer.data, safe=False)

