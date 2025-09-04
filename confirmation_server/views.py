from django.shortcuts import render
from django.views import generic


class IndexView(generic.ListView):
    template_name = "confirmation_server/index.html"
    context_object_name = "confirmation_server_landing"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return True