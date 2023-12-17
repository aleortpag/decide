from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

import pandas as pd

from django.core.exceptions import ValidationError

class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)


class CensusGroup(models.Model):
    name = models.CharField(max_length=200)
    users = ArrayField(models.PositiveIntegerField(), default=list, blank=True)
    voting = models.PositiveIntegerField()

    def clean(self):
        super().clean()

        for user_id in self.users:
            if not User.objects.filter(id=user_id).exists():
                raise ValidationError(f"El usuario con ID {user_id} no existe")
            
    def save(self):
        for u in self.users:
            Census.objects.get_or_create(voter_id=u, voting_id=self.voting)
        super().save()

    def __str__(self):
        return self.name
    
class CensusImport(models.Model):
    file = models.FileField()

    def save(self):

        excel = pd.read_excel(self.file)

        for i,j in excel.iterrows():
            voter = j['voter_id']
            voting = j['voting_id']
            
            if not Census.objects.filter(voter_id=voter, voting_id=voting).exists():
                census = Census(voter_id=voter, voting_id=voting)
                census.save()

        super().save()