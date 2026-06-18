from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.utils import timezone
import calendar as cal_mod
from .models import Calendar, Event


def planner_home(request):
    now = timezone.now()
    year = int(request.GET.get("year", now.year))
    month = int(request.GET.get("month", now.month))

    first_day = datetime(year, month, 1, tzinfo=timezone.get_current_timezone())
    if month == 12:
        last_day = datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone())
    else:
        last_day = datetime(year, month + 1, 1, tzinfo=timezone.get_current_timezone())

    events = Event.objects.filter(
        start_time__gte=first_day,
        start_time__lt=last_day,
    )

    cal_days = cal_mod.monthcalendar(year, month)
    weeks = []
    for week in cal_days:
        day_list = []
        for day in week:
            if day == 0:
                day_list.append(None)
            else:
                date = datetime(year, month, day).date()
                day_events = [e for e in events if e.start_time.date() == date]
                day_list.append({"day": day, "date": date, "events": day_events})
        weeks.append(day_list)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    month_names = [
        "", "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember",
    ]

    return render(
        request,
        "planner/planner.html",
        {
            "weeks": weeks,
            "month_name": month_names[month],
            "year": year,
            "month": month,
            "prev_month": prev_month,
            "prev_year": prev_year,
            "next_month": next_month,
            "next_year": next_year,
            "today": now.date(),
            "events": events,
        },
    )


@login_required
def event_create(request):
    if request.method == "POST":
        calendar, _ = Calendar.objects.get_or_create(
            user=request.user, defaults={"name": "Mein Kalender"}
        )
        Event.objects.create(
            calendar=calendar,
            title=request.POST.get("title"),
            description=request.POST.get("description", ""),
            location=request.POST.get("location", ""),
            start_time=request.POST.get("start_time"),
            end_time=request.POST.get("end_time"),
            all_day=request.POST.get("all_day") == "on",
            color=request.POST.get("color", "#4285f4"),
        )
        return redirect("planner_home")
    return render(request, "planner/event_form.html")


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, calendar__user=request.user)
    event.delete()
    return redirect("planner_home")
