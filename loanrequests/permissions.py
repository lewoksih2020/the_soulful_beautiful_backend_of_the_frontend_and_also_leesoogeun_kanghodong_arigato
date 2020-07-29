from rest_framework import permissions
import re

class IsauthorsenderOrModOrAdminOrReadOnly(permissions.BasePermission):
    """
    Only the poster, moderators of this sub, or admins can edit/delete a post
    """
    message = ("You can only modify this Loanrequest if you are the authorsender, " +
            "a moderator of this subReddit, or an admin.")
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        user = request.user
        loanrequest_sub_moderators = obj.subreddit.moderators.all()

        is_authorsender = True if user == obj.authorsender else False
        mod = True if user in loanrequest_sub_moderators else False
        admin = True if user.is_staff else False
        
        
        return is_authorsender or admin or mod
        
