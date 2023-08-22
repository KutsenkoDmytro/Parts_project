from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Entry



@login_required
def entry_detail(request, entry_id):
    entry = Entry.objects.get(id=entry_id)

    context = {'entry': entry}
    return render(request, 'entry/entry_detail.html', context)