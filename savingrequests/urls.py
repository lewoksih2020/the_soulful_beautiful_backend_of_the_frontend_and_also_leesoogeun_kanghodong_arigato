from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('', views.SavingrequestListView.as_view(), name='savingrequest-list'),
    path('<int:pk>/', views.SavingrequestDetailView.as_view(), name='savingrequest-detail'),
    path(
        'subreddit-list/<slug:sub_title>/',
        views.SubSavingrequestListView.as_view(),
        name='sub-savingrequest-list'
    ),
    path(
        'user-savingrequest-list/<slug:username>/',
        views.UserSavingrequestListView.as_view(),
        name='user-savingrequest-list'
    ),


    path(
        'create/<slug:sub_title>/',
        views.SavingrequestToSubredditView.as_view(),
        name='create-savingrequest'
    ),

    path(
        'create/<slug:username>/<slug:sub_title>/',
        views.SavingrequestToSubredditWithUsernameParamView.as_view(),
        name='create-savingrequest'
    )
]

urlpatterns = format_suffix_patterns(urlpatterns)
