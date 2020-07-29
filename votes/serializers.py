from rest_framework import serializers, exceptions

from .models import CommentVote, LoanrequestVote
from comments.models import Comment, Loanrequest


# http://localhost:8000/vote/


class VoteSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        try:
            defaults = {'vote_type': validated_data.pop('vote_type')}
        except KeyError:
            raise exceptions.ValidationError("vote_type is a required field")

        vote, created = self.Meta.model.objects.get_or_create(
            **validated_data,
            defaults=defaults
        )
        # need to unvote if duplicating a previous vote
        if not created:
            if vote.vote_type == defaults['vote_type']:
                vote.vote_type = 0
            else:
                vote.vote_type = defaults['vote_type']
            vote.save()
        return vote


class CommentVoteSerializer(VoteSerializer):
    comment = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all()
    )

    class Meta:
        model = CommentVote
        fields = (
            'vote_type', 'comment',
        )


class LoanrequestVoteSerializer(VoteSerializer):
    loanrequest = serializers.PrimaryKeyRelatedField(
        queryset=Loanrequest.objects.all()
    )

    class Meta:
        model = LoanrequestVote
        fields = (
            'vote_type', 'loanrequest',
        )
