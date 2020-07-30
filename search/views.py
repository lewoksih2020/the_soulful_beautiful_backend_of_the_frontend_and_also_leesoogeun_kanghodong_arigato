from rest_framework.response import Response
from rest_framework.views import APIView

from loanrequests.models import Loanrequest
from loanrequests.serializers import LoanrequestSerializer
from redditors.models import User
from redditors.serializers import UserSerializer
from savingrequests.models import Savingrequest
from savingrequests.serializers import SavingrequestSerializer
from subs.models import Sub
from subs.serializers import SubSerializer


class SearchView(APIView):
    """
    Very simple search view, takes a single GET query param and
    searches database for post, sureddit and users that contain
    that text. It then returns a serialized list of for each.
    In the case of Posts the pks are returned, for Subreddits and users
    the title and username are returned.
    """
    http_method_names=['get']
    
    def get(self, request, format=None, **kwargs):

        search_term = request.GET.get('q', '')
    
        serializer_context = {
            'request': request
        }
            
        loanrequests = LoanrequestSerializer(
            Loanrequest.objects.filter(title__icontains=search_term),
            many=True,
            context=serializer_context
        )
        savingrequests = SavingrequestSerializer(
            Savingrequest.objects.filter(title__icontains=search_term),
            many=True,
            context=serializer_context
        )
        users = UserSerializer(
            User.objects.filter(username__icontains=search_term),
            many=True,
            context=serializer_context
        )
        subreddits = SubSerializer(
            Sub.objects.filter(title__icontains=search_term),
            many=True,
            context=serializer_context
        )

        data = {
            'loanrequests': loanrequests.data,
            'savingrequests': savingrequests.data,
            'users': users.data,
            'subreddits': subreddits.data,
        }
        
        return Response(data=data)
