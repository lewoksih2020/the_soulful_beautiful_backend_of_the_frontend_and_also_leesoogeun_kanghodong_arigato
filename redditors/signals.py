from django.db.models import signals, Sum
from django.dispatch import receiver

from redditors.models import User
from votes.models import CommentVote, LoanrequestVote


@receiver(signals.post_save, sender=CommentVote)
@receiver(signals.post_save, sender=LoanrequestVote)
def karma_on_comment_vote(sender, instance, **kwargs):
    """
    On a vote creation or update, make the appropriate change to user karma.
    
    TODO: Now I wish that I hadn't made the vote class abstract. I could
    get away with one aggregate query. Should investigate if migrating to a
    multi-table inheritance for votes would cause any problems.
    
    Alternatively I could probably come up with a more complex but
    efficient way to do this with incrementing for each vote change.
    This has become a little inefficient but it's a more difficult problem
    than it seems.
    
    Another idea that could make this easier is to recognize that reddit
    separates karma into comment and post karma, we could make the User
    model reflect that and then handle each separately here.
    """

    # Need the poster of the comment or vote.
    if sender == CommentVote:
        authorsender = instance.comment.authorsender
    elif sender == LoanrequestVote:
        authorsender = instance.post.authorsender

    comment_karma = CommentVote.objects.filter(
        comment__authorsender_id=authorsender.pk
    ).aggregate(Sum('vote_type'))["vote_type__sum"] or 0
    loanrequest_karma = LoanrequestVote.objects.filter(
        loanrequest__authorsender_id=authorsender.pk
    ).aggregate(Sum('vote_type'))["vote_type__sum"] or 0

    authorsender.karma = loanrequest_karma + comment_karma
    authorsender.save()
