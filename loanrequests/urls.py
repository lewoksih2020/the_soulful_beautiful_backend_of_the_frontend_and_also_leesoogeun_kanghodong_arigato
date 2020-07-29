from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.LoanrequestListView.as_view(), name='loanrequest-list'),
    path('<int:pk>/', views.LoanrequestDetailView.as_view(), name='loanrequest-detail'),
    path(
        'subreddit-list/<slug:sub_title>/',
        views.SubLoanrequestListView.as_view(),
        name='sub-loanrequest-list'
    ),
    path(
        'user-loanrequest-list/<slug:username>/',
        views.UserLoanrequestListView.as_view(),
        name='user-loanrequest-list'
    ),


    path(
        'create/<slug:sub_title>/',
        views.LoanrequestToSubredditView.as_view(),
        name='create-loanrequest'
    ),

    path(
        'create/<slug:username>/<slug:sub_title>/',
        views.LoanrequestToSubredditWithUsernameParamView.as_view(),
        name='create-loanrequest'
    )
]

urlpatterns = format_suffix_patterns(urlpatterns)
