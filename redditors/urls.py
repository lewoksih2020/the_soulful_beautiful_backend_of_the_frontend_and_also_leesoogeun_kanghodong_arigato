from django.urls import path, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken.views import obtain_auth_token

from redditors.views import account_properties_view, update_account_view
from . import views

urlpatterns = [
    path('', views.UserListView.as_view(), name='user-list'),
    path('properties/', account_properties_view, name="user-properties"),
    path('properties/update', update_account_view, name="update"),

    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('create/', views.UserCreateView.as_view(), name='user-create'),
    path('<slug:username>/', views.UserDetailView.as_view(), name='user-detail'),

    path(
        'sub-user-list/<slug:subreddit_name>/',
        views.SubUserListView.as_view(),
        name='sub-user-list'
    ),
    path(
        'profile/<slug:username>/',
        views.UserProfileDetailView.as_view(),
        name='user-profile'
    )
    # path(
    #     'profile/<slug:username>/',
    #     views.UserProfileDetailView.as_view(),
    #     name='user-profile'
    # )
]

urlpatterns = format_suffix_patterns(urlpatterns)
