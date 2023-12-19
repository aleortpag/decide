from django.views.generic import TemplateView
from census.models import Census
from voting.models import Voting


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
                votacion['type'] = v.voting_type
                votings.append(votacion)
        context['votings'] = votings
        return context

    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
