from django.db import models
from base.models import BigBigField


class Vote(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()
    voted = models.DateTimeField(auto_now=True)

    a = BigBigField()
    b = BigBigField()

    def __str__(self):
        return 'voting_id:' + str(self.voting_id) + ', voter_id:' + str(self.voter_id) + ', voted:' + str(self.voted)
