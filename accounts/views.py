import jwt
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import (DjangoUnicodeDecodeError, smart_bytes,
                                   smart_str)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, views, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import (BlacklistedToken,
                                             OutstandingToken, RefreshToken)

from .permissions import IsNotAuthenticated
from .serializers import (ChangePasswordSerializer,
                          EmailVerificationSerializer, LogoutSerializer,
                          ResetPasswordEmailRequestSerializer,
                          SetNewPasswordSerializer, UserSerializer)
from .utils import Util


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    Abovementioned actions can be performed by request user or 
    by staff on any user.
    
    password fields applies only to creating new user,
    to change password use change password endopint
    """
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        This method ensures that only unauthenticated user can regiser
        a new account. Action 'list' also retained in this permission
        so register form is still available in browseable api, get_queryset
        method ensures that no user detail could be listed.
        """
        if self.action in ('create',):
            permission_classes = [IsNotAuthenticated]
        elif self.action in ('list',):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(username=user)
        
    def create(self, request, *args, **kwargs):
        """
        Override of create method to send activation email
        """
        user = request.data
        serializer = self.get_serializer(data=user)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user_data = serializer.data
        user = User.objects.get(username=user_data['username'])
        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relative_link = reverse('email-verify')
        absurl = 'http://'+current_site+relative_link+"?token="+str(token)
        email_body = 'Hi '+user.username + \
            ' Use the link below to verify your email \n' + absurl
        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}
        
        Util.send_email(data)
        return Response(serializer.data, 
                        status=status.HTTP_201_CREATED, 
                        headers=headers)
        
                
    def perform_destroy(self, instance):
        """
        Override of destroy method to perform soft delete
        """
        instance.is_active = False
        instance.save()
        

# class ChangePasswordView(generics.UpdateAPIView):
#     """
#     View that enables changing password by request user
#     """
#     queryset = User.objects.all()
#     permission_classes = [IsAuthenticated]
#     serializer_class = ChangePasswordSerializer
        
        
# class VerifyEmail(views.APIView):
#     """
#     View that enables email verification
#     """
#     serializer_class = EmailVerificationSerializer
    
#     token_param_config = openapi.Parameter(
#         'token', in_=openapi.IN_QUERY,
#         description='Description',
#         type=openapi.TYPE_STRING)
    
#     @swagger_auto_schema(manual_parameters=[token_param_config])
#     def get(self, request):
#         token = request.GET.get('token')
#         try:
#             payload = jwt.decode(token, 
#                                 settings.SECRET_KEY, 
#                                 algorithms='HS256')
#             user = User.objects.get(id=payload['user_id'])
#             if not user.is_active:
#                 user.is_active = True
#                 user.save()
#             return Response({'account': 'Successfully activated'}, 
#                             status=status.HTTP_200_OK)
#         except jwt.ExpiredSignatureError as identifier:
#             return Response({'error': 'Activation Expired'}, 
#                             status=status.HTTP_400_BAD_REQUEST)
#         except jwt.exceptions.DecodeError as identifier:
#             return Response({'error': 'Invalid token'}, 
#                             status=status.HTTP_400_BAD_REQUEST)
         

# class RequestPasswordResetEmail(generics.GenericAPIView):
#     """
#     View to type email to reset password
#     """
#     serializer_class = ResetPasswordEmailRequestSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)

#         email = request.data['email']

#         if User.objects.filter(email=email).exists():
#             user = User.objects.get(email=email)
#             uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
#             token = PasswordResetTokenGenerator().make_token(user)
#             current_site = get_current_site(
#                 request=request).domain
#             relativeLink = reverse(
#                 'password-reset-confirm', kwargs={
#                     'uidb64': uidb64, 'token': token
#                     }
#                 )
#             absurl = 'http://'+current_site + relativeLink
#             email_body = 'Hello, \n Use link below to reset your password  \n' + absurl
#             data = {'email_body': email_body, 'to_email': user.email,
#                     'email_subject': 'Reset your passsword'}
#             Util.send_email(data)
#         return Response({'success': 
#             'We have sent you a link to reset your password'}, 
#                         status=status.HTTP_200_OK)


# class PasswordTokenCheckAPI(generics.GenericAPIView):
#     """
#     View with credentials to reset password
#     """
#     serializer_class = SetNewPasswordSerializer

#     def get(self, request, uidb64, token):

#         try:
#             id = smart_str(urlsafe_base64_decode(uidb64))
#             user = User.objects.get(id=id)

#             if not PasswordResetTokenGenerator().check_token(user, token):
#                 return Response({
#                     'error': 'Token is not valid, please request a new one'}, 
#                                 status=status.HTTP_401_UNAUTHORIZED
#                                 )

#             return Response({
#                 'success': True, 
#                 'message': 'Credentials Valid', 
#                 'uidb64': uidb64, 
#                 'token': token
#                 }, 
#                             status=status.HTTP_200_OK
#                             )

#         except DjangoUnicodeDecodeError as identifier:
#             if not PasswordResetTokenGenerator().check_token(user):
#                 return Response({
#                     'error': 'Token is not valid, please request a new one'
#                     }, 
#                     status=status.HTTP_401_UNAUTHORIZED
#                     )


# class SetNewPasswordAPIView(generics.GenericAPIView):
#     """
#     View to setting new password
#     """
#     serializer_class = SetNewPasswordSerializer

#     def patch(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         return Response(
#             {'success': True, 'message': 'Password reset success'},
#             status=status.HTTP_200_OK)      

class LogoutView(APIView):
    """
    View for logging out by blacklisting a currnetly used token.
    """
    
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    
class LogoutAllView(APIView):
    """
    View for logging out by blacklisting all outstanding tokens
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
