import factory
import random

from votes.models import CommentVote, LoanrequestVote

class CommentVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentVote
        
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        vote_ratio = kwargs.pop('vote_ratio', 0.75)
        kwargs['vote_type'] = (CommentVote.UPVOTE
            if random.random() <= vote_ratio
            else CommentVote.DOWNVOTE
        )
        return super()._create(model_class, *args, **kwargs)
        
class LoanrequestVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LoanrequestVote
        
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        vote_ratio = kwargs.pop('vote_ratio', 0.75)
        kwargs['vote_type'] = (LoanrequestVote.UPVOTE
            if random.random() <= vote_ratio
            else LoanrequestVote.DOWNVOTE
        )
        return super()._create(model_class, *args, **kwargs)
        
