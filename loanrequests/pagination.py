# from rest_framework.pagination import LimitOffsetPagination
#
#
# # class PostListPagination(LimitOffsetPagination):
from rest_framework.pagination import PageNumberPagination


class LoanrequestListPagination(PageNumberPagination):
    # default_limit = 20
    # default_limit = 3
    # max_limit = 100
    page_size = 10

    # def get_next_link(self):
    #     url = super().get_next_link()
    #     return replace_query_param(url, self.limit.qu)
