from rest_framework import generics, serializers
from rest_framework import status, exceptions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated)
from rest_framework.response import Response
from rest_framework.views import APIView

from loanrequests.pagination import LoanrequestListPagination
from log import setup_logger
from redditors.permissions import IsLoggedInOrReadOnly
from subs.models import Sub
from subs.serializers import SubSerializer
from .models import User
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    AccountPropertiesSerializer, AccountPropertiesUpdateSerializer)

logger = setup_logger()


class UserListView(generics.ListAPIView):
    # queryset = User.objects.all()
    queryset = User.objects.get_queryset().order_by('pk')
    serializer_class = UserSerializer
    pagination_class = LoanrequestListPagination
    # pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('username',)
    permission_classes = (IsAuthenticatedOrReadOnly,)


class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = (IsLoggedInOrReadOnly,)
    lookup_field = 'username'

    def get_serializer_class(self):
        """
        Probably should be using a view set but for now
        just pick a serializer based on the http method.
        """
        if self.request.method.lower() == "patch":
            return UserUpdateSerializer
        return UserSerializer


@api_view(['GET', ])
@permission_classes((IsAuthenticated,))
def account_properties_view(request):
    logger.info(f"{request}")
    try:
        user = request.user
        logger.info(f"{request.user} --> try")
    except User.DoesNotExist:
        logger.info(f"{request.user} --> except")
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        logger.info("Inside Get")
        serializer = AccountPropertiesSerializer(user)
        return Response(serializer.data)


@api_view(['PUT', ])
@permission_classes((IsAuthenticated,))
def update_account_view(request):
    try:
        user = request.user
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = AccountPropertiesUpdateSerializer(user, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = 'Account update success'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPropertiesDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # lookup_field = 'username'
    # lookup_field = 'username'
    serializer_class = AccountPropertiesSerializer


class SubUserListView(ListAPIView):
    """
    For a particular subreddit return list of all subscribed users.
    """
    serializer_class = UserSerializer
    pagination_class = LoanrequestListPagination
    # pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('username', 'email')

    def get_queryset(self):

        subreddit_name = self.kwargs.get('subreddit_name', None)

        # if username.lower() in Sub.pseudo_subreddits:
        #     qs = getattr(
        #         self,
        #         "get_{}_queryset".format(subreddit_title.lower())
        #     )()

        # make sure the subreddit exists
        try:
            subreddit = Sub.objects.get(title=subreddit_name)
        except Sub.DoesNotExist:
            message = _("The '{}' Sub does not exist".format(
                subreddit_name
            ))
            raise exceptions.NotFound(message)
        # qs = user.subs.all()
        qs = subreddit.members.get_queryset().order_by('pk')
        return qs


class UserProfileDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # lookup_field = 'username'
    lookup_field = 'username'
    serializer_class = UserProfileSerializer


class UserCreateView(generics.CreateAPIView):
    # queryset = User.objects.all()
    # serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        data = {}
        email = request.data.get('email', '0').lower()
        if validate_email(email) is not None:
            data['error_message'] = 'That email is already in use.'
            data['response'] = 'Error'
            return Response(data)

        username = request.data.get('username', '0')
        if validate_username(username) is not None:
            data['error_message'] = 'That username is already in use.'
            data['response'] = 'Error'
            return Response(data)

        serializer = UserCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            data['response'] = 'successfully registered new user.'
            data['email'] = user.email
            data['username'] = user.username
            data['location'] = user.location
            data['first_name'] = user.first_name
            data['savingtarget'] = user.savingtarget
            data['is_verified_aadharcard'] = user.is_verified_aadharcard
            data['aadharcard'] = user.aadharcard
            data['last_name'] = user.last_name
            data['age'] = user.age
            data['pk'] = user.pk
            token, _ = Token.objects.get_or_create(user=user)
            data['token'] = token.key
        else:
            data = serializer.errors
        return Response(data)


def validate_email(email):
    account = None
    try:
        account = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    if account is not None:
        return email


def validate_username(username):
    account = None
    try:
        account = User.objects.get(username=username)
    except User.DoesNotExist:
        return None
    if account is not None:
        return username


class UserLogoutView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def post(self, request, *args, **kwargs):
        try:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )

        loanrequests = serializers.SerializerMethodField()
        savingrequests = serializers.SerializerMethodField()





        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        subs = SubSerializer(user.subs.all(),
                             many=True,
                             context={'request': request}
                             )
        moderated_subs = SubSerializer(
            user.moderated_subs.all(),
            many=True,
            context={'request': request}
        )
        return Response({
            'token': token.key,
            'username': user.username,
            'email': user.email,
            'location': user.location,
            'first_name': user.first_name,
            'savingtarget': user.savingtarget,
            'aadharcard': user.aadharcard,
            'is_verified_aadharcard': user.is_verified_aadharcard,
            'last_name': user.last_name,
            'age': user.age,
            'pk': user.pk,
            'subs': subs.data,
            'moderated_subs': moderated_subs.data
        })
