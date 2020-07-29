from django.db.models import Sum
from django.utils.translation import gettext as _
from rest_framework import status, exceptions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from loanrequests.pagination import LoanrequestListPagination
from redditors.models import User
from subs.models import Sub
from .models import Loanrequest
from .permissions import IsauthorsenderOrModOrAdminOrReadOnly
from .serializers import LoanrequestSerializer


class LoanrequestListView(ListAPIView):
    """
    Standard list view for loanrequests
    
    query parameter: username
    """
    # queryset = Post.objects.all()
    queryset = Loanrequest.objects.get_queryset().order_by('pk')
    serializer_class = LoanrequestSerializer
    pagination_class = LoanrequestListPagination
    # pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body')
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_serializer_context(self):
        """
        It will really speed up some vote lookups in the
        serializer if we can turn a username into a user_pk at this point.
        This is only relevant if the consumer provides a get param 'username'
        """
        context = super().get_serializer_context()
        username = self.request.query_params.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return context
            context['loanrequest_user_pk'] = user.pk
        return context


class LoanrequestDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Loanrequest.objects.all()
    serializer_class = LoanrequestSerializer
    permission_classes = (IsauthorsenderOrModOrAdminOrReadOnly,)


class UserLoanrequestListView(ListAPIView):
    """
    For a particular user return list of all subscribed subreddits.
    """
    serializer_class = LoanrequestSerializer
    pagination_class = LoanrequestListPagination
    # pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body')

    def get_queryset(self):

        username = self.kwargs.get('username', None)

        # if username.lower() in Sub.pseudo_subreddits:
        #     qs = getattr(
        #         self,
        #         "get_{}_queryset".format(subreddit_title.lower())
        #     )()

        # make sure the subreddit exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            message = _("The '{}' user does not exist".format(
                username
            ))
            raise exceptions.NotFound(message)
        # qs = user.subs.all()
        qs = user.loanrequests.get_queryset().order_by('pk')
        return qs


class LoanrequestToSubredditView(CreateAPIView):
    serializer_class = LoanrequestSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        """
        Need to grab the subreddit from the url and the authenticated
        user from the request and add them to the serializer data
        NOTE: I wonder if there is a better way to do this, copying data
        is a bummer but dont want these to be read_only
        """
        subreddit_title = kwargs["sub_title"]
        if subreddit_title.lower() in Sub.pseudo_subreddits.keys():
            message = _((
                "You can't create a post to the "
                "'{}' subreddit".format(subreddit_title)
            ))
            return Response(
                {"detail": message},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            subreddit = Sub.objects.get(title=subreddit_title)
        user = self.request.user
        data = request.data.copy()
        data["subreddit"] = subreddit.title
        data["authorsender"] = user.username
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class LoanrequestToSubredditWithUsernameParamView(CreateAPIView):
    serializer_class = LoanrequestSerializer

    # permission_classes = (IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        """
        Need to grab the subreddit from the url and the authenticated
        user from the request and add them to the serializer data
        NOTE: I wonder if there is a better way to do this, copying data
        is a bummer but dont want these to be read_only
        """
        subreddit_title = kwargs["sub_title"]
        # username = kwargs["username"]
        username = self.kwargs.get('username', None)

        # if username.lower() in Sub.pseudo_subreddits:
        #     qs = getattr(
        #         self,
        #         "get_{}_queryset".format(subreddit_title.lower())
        #     )()

        # make sure the subreddit exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            message = _("The '{}' user does not exist".format(
                username
            ))
            raise exceptions.NotFound(message)

        if subreddit_title.lower() in Sub.pseudo_subreddits.keys():
            message = _((
                "You can't create a post to the "
                "'{}' subreddit".format(subreddit_title)
            ))
            return Response(
                {"detail": message},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            subreddit = Sub.objects.get(title=subreddit_title)

        # user = self.request.user
        data = request.data.copy()
        data["subreddit"] = subreddit.title
        data["authorsender"] = user.username
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


class SubLoanrequestListView(ListAPIView):
    """
    For a particular sub return list of all loanrequests.
    Posts can be ordered with optional GET parameter 'orderby'.
    By default they are ordered by most popular.
    
    query parameter: orderby
    """
    serializer_class = LoanrequestSerializer
    pagination_class = LoanrequestListPagination
    # pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('title', 'body')

    # def get_sort_function(self):
    #     """
    #     Given an api sort description (e.g. 'popular' or 'new') return
    #     a key function that can be used in sort based on the acutal
    #     model attributes nomenclature.
    #     """
    #     sort_functions = {
    #         'best': (lambda post: -post.upvotes),
    #         'new': (lambda post: (timezone.now() - post.created))
    #     }
    #     api_sort_key = self.request.query_params.get('orderby', 'best')
    #     return sort_functions.get(api_sort_key, sort_functions['best'])

    def get_queryset(self):
        """
        Check if loanrequests are requested from a psuedo-subreddit
        or ensure that the requested subreddit exists.
        Either way order the subreddit too.
        NOTE: At this point can't sort with qs.order_by because
        upvotes are not a column of the post table in db.
        """
        subreddit_title = self.kwargs.get('sub_title', None)

        if subreddit_title.lower() in Sub.pseudo_subreddits:
            qs = getattr(
                self,
                "get_{}_queryset".format(subreddit_title.lower())
            )()
        else:
            # make sure the subreddit exists
            try:
                subreddit = Sub.objects.get(title=subreddit_title)
            except Sub.DoesNotExist:
                message = _("The '{}' subreddit does not exist".format(
                    subreddit_title
                ))
                raise exceptions.NotFound(message)
            # qs = subreddit.loanrequests.all()
            qs = subreddit.loanrequests.get_queryset().order_by('pk')
        return qs

    def get_home_queryset(self):
        """
        Create a list of loanrequests for a 'home' subreddit on the fly.
        This will depend on whether the user is signed in or not.
        If they are authenticated then only select loanrequests from
        thier subscribed subreddits. Otherwise just return a list
        of all loanrequests.
        """
        if self.request.user and self.request.user.is_authenticated:
            return Loanrequest.objects.filter(
                # subreddit__in=self.request.user.subs.all()
                subreddit__in=self.request.user.subs.get_queryset().order_by('pk')
            )

        # return all loanrequests if unauthed
        # return Post.objects.all()
        return Loanrequest.objects.get_queryset().order_by('pk')

    def get_popular_queryset(self):
        """
        Create a list of loanrequests popular loanrequests on the fly that serves as the
        'Popular' psuedo subreddit.
        """
        # Arbitrary popularity limit
        popularity_limit = 1

        return Loanrequest.objects.annotate(
            custom_upvotes=Sum("votes__vote_type")
        ).filter(custom_upvotes__gt=popularity_limit)

    def get_all_queryset(self):
        """
        Get the list of loanrequests on the fly for the psuedo-subreddit 'All'.
        NOTE: At this point I'm not really sure what the actual reddit
        difference is between all and popular so I am just going to
        use popular for now.
        """
        # return Post.objects.all()
        return Loanrequest.objects.get_queryset().order_by('pk')
