from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.translation import gettext as _
from rest_framework import serializers

from redditors.models import User
from subs.models import Sub
from votes.models import LoanrequestVote
from .models import Loanrequest


class LoanrequestSerializer(serializers.ModelSerializer):
    authorsender = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',

    )

    subreddit = serializers.SlugRelatedField(
        queryset=Sub.objects.all(),
        slug_field='title',

    )

    voters = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='username'

    )

    subreddit_title = serializers.SerializerMethodField()
    authorsender_username = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    updated = serializers.SerializerMethodField()
    vote_state = serializers.SerializerMethodField()

    class Meta:
        model = Loanrequest
        fields = ('pk', 'created', 'updated', 'title', 'body',
                  'upvotes', 'subreddit', 'authorsender', 'subreddit_title',
                  'authorsender_username', 'vote_state', 'voters')

    def validate(self, data):
        """
        Ensure that the user is a member of the subreddit
        being posted to
        """
        authorsender = data.get("authorsender")
        subreddit = data.get("subreddit")

        # Only relevant when doing a creation, not an update
        if authorsender and subreddit:
            # make sure they aren't trying to create a post to a pseudo subreddit
            if subreddit.title.lower() in Sub.pseudo_subreddits.keys():
                message = _(
                    ("You can't create a Loanrequest to the "
                     "'{}' subreddit.".format(subreddit.title))
                )
                raise serializers.ValidationError(message)
            if not subreddit in authorsender.subs.all():
                message = _("You must be a member of the subreddit to Loanrequest here.")
                raise serializers.ValidationError(message)

        return data

    def get_subreddit_title(self, obj):
        return obj.subreddit.title

    def get_authorsender_username(self, obj):
        return obj.authorsender.username

    def get_created(self, obj):
        return naturaltime(obj.created)

    def get_updated(self, obj):
        return naturaltime(obj.updated)

    def get_vote_state(self, obj):
        """
        If a user is authenticated, look up whether they have voted on this post
        before.
        """
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            try:
                vote = obj.votes.all().get(user_id=request.user.pk)
                return vote.vote_type
            except LoanrequestVote.DoesNotExist:
                pass
        return 0
