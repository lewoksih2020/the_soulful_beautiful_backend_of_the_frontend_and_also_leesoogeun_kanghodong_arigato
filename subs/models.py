from django.db import models
from django.core.exceptions import FieldError


class Sub(models.Model):
    pseudo_subreddits = {
        'popular': "The most popular loanrequests from all over reReddit are collected here.",
        'home': (
            "A collection of loanrequests from the subreddits "
            "you're interested in. Your own personal reReddit view."
        ),
        'all': "The most active loanrequests from all over reReddit.",
    }

    created = models.DateTimeField(auto_now_add=True)
    title = models.SlugField(max_length=40, unique=True)
    description = models.CharField(max_length=1000, blank=True)

    @property
    def memberscount(self):

        return len(self.members.all())

    @property
    def moderatorscount(self):

        return len(self.moderators.all())

    moderators = models.ManyToManyField(
        to='redditors.User',
        related_name='moderated_subs')

    # ManyToManyField to User, related_name="members"
    # backward FK loanrequests from Post

    def __str__(self):
        return "subReddit: {}".format(self.title)

    def save(self, *args, **kwargs):
        """
        Prevent creation of subreddits that use names
        needed for the psuedo subreddits
        """
        if self.title.lower() in self.pseudo_subreddits:
            message = "The subreddit title '{}' is reserved".format(self.title)
            raise FieldError(message)
        else:
            super().save(*args, **kwargs)
