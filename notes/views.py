from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Note


@login_required
def notes_home(request):
    notes = Note.objects.filter(user=request.user, is_archived=False)
    return render(request, "notes/notes.html", {"notes": notes})


@login_required
def note_create(request):
    note = Note.objects.create(user=request.user)
    return redirect("notes_home")


@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == "POST":
        note.title = request.POST.get("title", "")
        note.content = request.POST.get("content", "")
        note.color = request.POST.get("color", "#ffffff")
        note.save()
        return redirect("notes_home")
    return JsonResponse({"ok": True})


@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.delete()
    return redirect("notes_home")


@login_required
def note_pin(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_pinned = not note.is_pinned
    note.save()
    return redirect("notes_home")


@login_required
def note_archive(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    note.is_archived = True
    note.save()
    return redirect("notes_home")
