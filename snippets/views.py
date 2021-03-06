from django.shortcuts import redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView,
    UpdateView
)
from django.utils.translation import ugettext as _
from django.http import Http404

from braces.views import LoginRequiredMixin

from snippets.models import Snippet
from snippets.forms import (
    CreateSnippetForm,
    UpdateSnippetForm
)

from .mixins import (
    SnippetOwnerRequiredOnDeleteMixin,
    SnippetOwnerRequiredOnUpdateMixin
)


class SnippetsView(LoginRequiredMixin, ListView):
   
    template_name = 'snippets/snippets.html'
    model = Snippet
    context_object_name = 'snippets'

    def get_queryset(self):
        return self.model.objects.filter(approved=True).order_by('-created')


class SnippetDetailsView(LoginRequiredMixin, DetailView):

    template_name = 'snippets/snippet_details.html'
    model = Snippet
    context_object_name = 'snippet'

    def get_context_data(self, **kwargs):
        context = super(SnippetDetailsView, self).get_context_data(**kwargs)
        context['snippet'].tags = context['snippet'].get_tags()
        return context

    def get(self, request, *args, **kwargs):
        # only allow the snippet to be viewed if it is already
        # approved or the current logged-in user is the author
        snippet = self.get_object()
        if snippet.approved or request.user ==  snippet.author:
            return super(SnippetDetailsView, self).get(request, *args, **kwargs)
        raise Http404
        

class CreateSnippetView(LoginRequiredMixin, CreateView):

    template_name = 'snippets/create.html'
    model = Snippet
    form_class = CreateSnippetForm

    def form_valid(self, form):
        snippet = form.save(commit=False)
        snippet.author = self.request.user
        return super(CreateSnippetView, self).form_valid(form)

    def get_success_url(self):
        return reverse('user_snippets', args=(self.request.user.profile.slug,))


class SnippetDeleteView(LoginRequiredMixin, SnippetOwnerRequiredOnDeleteMixin, DeleteView):

    model = Snippet
    success_url = reverse_lazy('snippets')


class SnippetUpdateView(LoginRequiredMixin, SnippetOwnerRequiredOnUpdateMixin, UpdateView):

    model = Snippet 
    template_name = 'snippets/update.html'
    context_object_name = 'snippet'
    form_class = UpdateSnippetForm

    def get_initial(self):
        obj = self.get_object()
        return {'tags': obj.tags.all()}


class MySnippetsView(LoginRequiredMixin, ListView):

    model = Snippet
    context_object_name = 'snippets'
    template_name = 'snippets/my_snippets.html'

    def get_queryset(self):
        return self.model.objects.filter(author=self.request.user).order_by('-created')





