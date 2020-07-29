from django.core.management.base import CommandError
from votes.management.commands._base_vote_command import VoteSeedCommandBase
import random

from votes.factory import LoanrequestVoteFactory
from redditors.models import User
from loanrequests.models import Loanrequest
    
class Command(VoteSeedCommandBase):
    help="Adds fake post votes to the database"
        
    def handle(self,*args, **options):
        n_votes = options['number']
        vote_ratio = options['vote_ratio']

        # Designed assuming relatively large batches of votes are made
        # just grab them all
        loanrequests = list(Loanrequest.objects_no_votes.all())
        users = list(User.objects.all())
        
        out = "Creating {} new post votes with a {} upvote ratio".format(
            n_votes,
            vote_ratio
        )
        self.stdout.write(out)
        for _ in range(n_votes):
            loanrequest = random.choice(loanrequests)
            user = random.choice(users)
            loanrequest_vote = LoanrequestVoteFactory.create(
                user=user,
                loanrequest=loanrequest,
                vote_ratio=vote_ratio
            )
            self.stdout.write("\t-- Voter: {}, Vote: {}".format(
                loanrequest_vote.user,
                loanrequest_vote.vote_type
            ))
