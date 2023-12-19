from django.db import models
from django.db.models import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import int_list_validator

from base import mods
from base.models import Auth, Key
from census.models import CensusGroup


class Question(models.Model):
    desc = models.TextField()

    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()
    preference = models.IntegerField(blank=True, null=True)

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)


class Voting(models.Model):

    VOTING_TYPES = [('preference', 'Preference-Based Voting'), ('normal', 'Normal voting')]

    voting_type = models.CharField(max_length=15, choices=VOTING_TYPES, default='normal',)

    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)
    preferences = models.CharField(validators=[int_list_validator], max_length=100)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    group = models.ForeignKey(CensusGroup, related_name='votings', null=True, blank=True, on_delete=models.SET_NULL)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [{"name": a.name, "url": a.url} for a in self.auths.all()],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        votes_format = []
        vote_list = []
        if self.voting_type == 'preference':
            for vote in votes:
                preferences = []
                for info in vote:
                    if info == 'a':
                        votes_format.append(vote[info])
                    if info == 'b':
                        votes_format.append(vote[info])
                    elif info == 'preference':
                        preferences.append(vote[info])
                votes_format.append(preferences)
                vote_list.append(votes_format)
                votes_format = []
        else:
            for vote in votes:
                for info in vote:
                    if info == 'a':
                        votes_format.append(vote[info])
                    if info == 'b':
                        votes_format.append(vote[info])
                vote_list.append(votes_format)
                votes_format = []
        return vote_list

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)

        if self.voting_type == 'preference':
            self.tally_preference_votes(votes)
            self.save()
        else:

            # first, we do the shuffle
            data = {"msgs": votes}
            response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                   response=True)
            if response.status_code != 200:
                # TODO: manage error
                pass

            # then, we can decrypt that
            data = {"msgs": response.json()}
            response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                    response=True)

            if response.status_code != 200:
                # TODO: manage error
                pass

            self.tally = response.json()
            self.save()

            self.do_postproc()

    def tally_preference_votes(self, votes):
        option_scores = {opt.number: 0 for opt in self.question.options.all()}
        weights = list(range(len(option_scores), 0, -1))
        for vote in votes:
            preferences = vote['preferences']
            for i, option_number in enumerate(preferences):
                option_scores[option_number] += weights[i]
        opts = []
        for opt_number, score in option_scores.items():
            opts.append({
                'option': self.question.options.get(number=opt_number).option,
                'number': opt_number,
                'votes': score
            })
        sorted_opts = sorted(opts, key=lambda x: x['votes'], reverse=True)
        self.tally = sorted_opts
        self.save()

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()

        opts = []

        for opt in options:
            if isinstance(tally, list):
                votes = tally.count(opt.number)
            else:
                votes = 0
            opts.append({
                'option': opt.option,
                'number': opt.number,
                'votes': votes
            })

        data = {'type': 'IDENTITY', 'options': opts}
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name
