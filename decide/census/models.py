from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError

class Census(models.Model):
    voting_id = models.PositiveIntegerField()
    voter_id = models.PositiveIntegerField()

    class Meta:
        unique_together = (('voting_id', 'voter_id'),)


class CensusGroup(models.Model):
    name = models.CharField(max_length=200)
    users = ArrayField(models.PositiveIntegerField(), default=list, blank=True)

    def clean(self):
        super().clean()

        for user_id in self.users:
            if not User.objects.filter(id=user_id).exists():
                raise ValidationError(f"El usuario con ID {user_id} no existe")

    def __str__(self):
        return self.name