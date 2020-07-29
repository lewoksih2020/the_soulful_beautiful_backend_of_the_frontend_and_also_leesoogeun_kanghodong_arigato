from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import (
    ListCreateAPIView, ListAPIView,
    RetrieveUpdateDestroyAPIView, UpdateAPIView,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from collections import defaultdict
from django.utils import timezone

from loanrequests.pagination import LoanrequestListPagination
from .models import Comment
from .serializers import (
    CommentSerializer, CommentTreeSerializer,
)
from redditors.models import User


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    """
    For edits of comments, 'deletes', or re-fetching a single comment.
    On delete the comment is not really deleted. Just as in
    reddit we overwrite the content and remove
    the reference to the poster. Votes, voters, and
    its creation date are preserved.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer.reddit_delete()
        return Response(serializer.data)


class CommentListView(ListCreateAPIView):
    """
    Standard list and create view for comments. The user must
    be authenticated to post/create a comment.
    """
    # queryset = Comment.objects.all()
    queryset = Comment.objects.get_queryset().order_by('pk')
    serializer_class = CommentSerializer
    pagination_class = LoanrequestListPagination
    # pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('body',)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        """
        You need to be authenticated to post a comment.
        Take that authenticated user and make them the poster
        """
        serializer.save(authorsender=self.request.user)


class LoanrequestCommentView(ListAPIView):
    """
    For a particular post returns all comments, paginated and in a nested,
    hierarchichal fashion.
    
    query parameter: orderby, username
    """
    queryset = Comment.objects.all()
    pagination_class = LoanrequestListPagination
    # pagination_class = PageNumberPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('body',)
    serializer_class = CommentTreeSerializer

    def get_sort_function(self):
        """
        Given an api sort description (e.g. 'popular' or 'new') return
        a key function that can be used in sort based on the acutal
        model attributes nomenclature.
        """
        sort_functions = {
            'best': (lambda comment: -comment.upvotes),
            'new': (lambda comment: (timezone.now() - comment.created)),
        }
        api_sort_key = self.request.query_params.get('orderby', 'best')
        return sort_functions.get(api_sort_key, sort_functions['best'])

    def get_queryset(self):
        """
        Narrows queryset to root comments on this post. Also
        orders depending on get parameter, default to popular.
        """
        loanrequest_pk = self.kwargs.get('loanrequest_pk', None)
        queryset = Comment.objects.filter(
            loanrequest__pk=loanrequest_pk,
            parent=None
        )
        # Can't use .order_by() in get_queryset because upvotes is not a db field
        # so wait until now to sort since we have a list
        # can't use inplace .sort either
        queryset = sorted(queryset, key=self.get_sort_function())
        return queryset

    def list(self, request, *args, **kwargs):
        root_comments = self.filter_queryset(self.get_queryset())
        comment_trees = []
        for root in root_comments:
            comment_trees.append(self.make_tree(root))
        return Response(comment_trees)

    def make_tree(self, root):
        children = defaultdict(list)
        for comment in root.get_descendants():
            children[comment.parent_id].append(comment)

        # For every parent, order the children according to the get parameter
        for child_list in children.values():
            child_list.sort(key=self.get_sort_function())

        context = self.get_serializer_context()
        context['children'] = children
        serializer = self.get_serializer_class()(root, context=context)
        return serializer.data
