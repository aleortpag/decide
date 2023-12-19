import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from census.models import Census
from voting.models import Voting

from base import mods

class AvailableVotingsView(TemplateView):
    template_name = 'user/availableVotings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        census = Census.objects.filter(voter_id = context['user_id'])
        votings = []
        for c in census:
            voting = Voting.objects.filter(id = c.voting_id)
            for v in voting:    
                votacion = {}
                votacion['id'] = v.id
                votacion['name'] = v.name
                votings.append(votacion)
        context['votings'] = votings
        return context

    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)