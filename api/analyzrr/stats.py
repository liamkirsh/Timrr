# -*- coding: utf-8 -*-
import datetime as dt
import re

from analyzrr import db
from selfspy import models, stats


APP_CLASSIFIERS = {
    'work': re.compile(
        r"|".join([
            r"iterm2",
            r"gitx",
            r"Python",
            r"System Preferences",
            r"Finder",
            r"Photoshop",
            r"Script Editor",
            r"Preview",
            r"Activity Monitor",
            r"Accessibility Inspector",
            r"Script Editor",
        ]),
        re.IGNORECASE),
    'personal': re.compile(
        r"|".join([
            r"Spotify",
            r"Franz",
            r"Whatsapp",
            r"AU Lab",
        ]),
        re.IGNORECASE),
}

WINDOW_CLASSIFIERS = {
    'work': re.compile(
        r"|".join([
            # generic work-related keywords
            r"debugger",
            r"documentation",
            r"python",
            r"man page",
            r"wxwidget",
            r"wxpython",
            # general work-related sites
            r"localhost",
            r"slack",
            r"google search",
            r"github",
            r"hack\w?zurich",
            r"stack overflow",
            r"super user",
            r"stack exchange",
            r"serverfault.com",
            r"stackexchange.com",
            r"stackoverflow.com",
            r"python.org",
            r"developer.apple.com",
            # Github page titles
            r"(Issues|at (master|[0-9a-f]{40})) · \w+/\w+",
            r"\w+/\w+: \w+",
            r"github.com",
        ]),
        re.IGNORECASE),
    'personal': re.compile(
        r"|".join([
            # general work-unrelated sites
            r"hacker news",
            r"news.ycombinator.com",
            r"soundcloud",
            r"twitter",
            r"xkcd",
            r"youtube",
            r"Facebook",
            r"facebook.com",
            r"reddit",
            r"mixcloud",
            r"news",
            r"memes",
            r"imgur",
            r"the verge",
        ]),
        re.IGNORECASE),
}

# IDLE_TIMEOUT = dt.timedelta(minutes=1)
IDLE_TIMEOUT = dt.timedelta(seconds=30)

def get_last_used_application(session):
    last_click = session.query(models.Click).order_by(models.Click.created_at.desc()).first()    
    last_key = session.query(models.Keys).order_by(models.Keys.created_at.desc()).first()

    last_interaction = last_click if last_click.created_at > last_key.created_at else last_key
    return last_interaction.process, last_interaction.window, last_interaction.created_at


def get_network_status(session, before=None):
    if before is None:
        before = dt.datetime.now()

    last_network_location = session.query(db.Network).filter(
        db.Network.created_at <= before
    ).order_by(db.Network.created_at.desc()).first()

    return last_network_location


def get_events_for_a_day(session, shift=0):
    assert shift <= 0, "can't look into the future!"
    delta = dt.timedelta(days=shift)

    start_of_day = dt.datetime.combine(dt.datetime.today(), dt.time()) + delta
    end_of_day = min(start_of_day + dt.timedelta(days=1, seconds=-1), dt.datetime.now())

    return get_events(session, start_of_day, end_of_day)


def get_events(session, start, end):
    assert start < end, "you mixed up the order, stupid!"

    events = []
    for model in [models.Click, models.Keys, db.Network]:
        events.extend(
            session
                .query(model)
                .filter(model.created_at.between(start, end))
                .order_by(model.created_at.desc())
                .all()
        )

    events.sort(key=lambda ev: ev.created_at)
    return events

def create_intervals(session, events):
    if not events:
        return []

    def create_new_interval(event, network):
        new_interval = {
            'process': event.process,
            'window': event.window,
            'network': network,
            'time_start': event.created_at,
            'time_end': event.created_at,
            'classification': 'undecided',
        }
        return new_interval

    current_event = events[0]
    current_network = get_network_status(session, before=current_event.created_at)

    intervals = [create_new_interval(current_event, current_network)]

    for event in events[1:]:
        if isinstance(event, db.Network):
            current_network = event
            continue

        if event.process is not current_event.process or event.window is not current_event.window:
            previous_interval = intervals[-1]
            previous_interval['time_end'] = current_event.created_at
            classify_interval(previous_interval, event.created_at)

            intervals.append(create_new_interval(event, current_network))

        current_event = event

    return intervals


def classify_interval(interval, time_next_event):
    classification = interval['classification'] = classify_event(
        interval['process'],
        interval['window'],
        interval['network'],
        interval['time_end'],
        time_next_event
    )
    return classification


def classify_event(process, window, network, time_end, time_next_event=None):
    if time_next_event is None:
        time_next_event = dt.datetime.now()

    is_idle = time_next_event - time_end > IDLE_TIMEOUT

    is_work_process = APP_CLASSIFIERS['work'].search(process.name) is not None
    is_work_window = WINDOW_CLASSIFIERS['work'].search(window.title) is not None
    is_work_app = is_work_process or is_work_window

    is_personal_process = APP_CLASSIFIERS['personal'].search(process.name) is not None
    is_personal_window = WINDOW_CLASSIFIERS['personal'].search(window.title)
    is_personal_app = is_personal_process or is_personal_window

    # XXX(fubu): In the following decision tree the conditions have to be met
    #   exactly, otherwise the decision has to fall through to "undecided".
    if network is None or network.action == "disconnect":
        # network=none && app=personal && idle=True  => "not-working"
        # network=none && app=personal && idle=False => "not-working"
        # network=none && app=work && idle=True      => "not-working"
        # network=none && app=work && idle=False     => "productive"
        if is_work_app:
            return "not-working" if is_idle else "productive"
        elif is_personal_app:
            return "not-working"

    elif network.location.kind == "personal":
        # network=personal && app=personal && idle=True  => "not-working"
        # network=personal && app=personal && idle=False => "not-working"
        # network=personal && app=work && idle=True      => "not-working"
        # network=personal && app=work && idle=False     => "productive"
        if is_work_app:
            return "not-working" if is_idle else "productive"
        elif is_personal_app:
            return "not-working"

    elif network.location.kind == "work":
        # network=work && app=personal && idle=True  => "unproductive"
        # network=work && app=personal && idle=False => "unproductive"
        # network=work && app=work && idle=True      => "unproductive"
        # network=work && app=work && idle=False     => "productive"
        if is_work_app:
            return "unproductive" if is_idle else "productive"
        elif is_personal_app:
            return "unproductive"

    return "undecided"


def flatten_intervals(intervals):
    if not intervals:
        return []

    def create_new_work_period(interval):
        new_period = {
            'from': interval['time_start'],
            'to': interval['time_end'],
            'type': interval['classification'],
            'name': "Optional"
        }
        return new_period

    current_interval = intervals[0]
    work_periods = [create_new_work_period(current_interval)]

    for interval in intervals[1:]:
        if interval['classification'] != current_interval['classification']:
            work_periods[-1]['to'] = current_interval['time_end']
            work_periods.append(create_new_work_period(interval))

        current_interval = interval

    return work_periods
