# -*- coding: utf-8 -*-
import datetime
import re

from analyzrr import db
from selfspy import models, stats


APP_CLASSIFIERS = {
    'work': re.compile(
        r"|".join([
            r".*term\d?",
            r"gitx",
            r"Python",
            r"^System Preferences$",
            r"^Finder$",
        ]),
        re.IGNORECASE),
    'personal': re.compile(
        r"|".join([
            r"^Spotify$",
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
            # general work-related sites
            r"localhost",
            r"stack overflow",
            r"google search",
            r"github",
            r"hack\w?zurich",
            # Github page titles
            r"(Issues|at (master|[0-9a-f]{40})) · \w+/\w+",
            r"\w+/\w+: \w+",
        ]),
        re.IGNORECASE),
    'personal': re.compile(
        r"|".join([
            # general work-unrelated sites
            r"hacker news",
            r"soundcloud",
            r"twitter",
            r"xkcd",
            r"youtube",
        ]),
        re.IGNORECASE),
}

IDLE_TIMEOUT = datetime.timedelta(minutes=5)

def get_last_used_application(session):
    last_click = session.query(models.Click).order_by(models.Click.created_at.desc()).first()    
    last_key = session.query(models.Keys).order_by(models.Keys.created_at.desc()).first()

    last_interaction = last_click if last_click.created_at > last_key.created_at else last_key
    return last_interaction.process, last_interaction.window, last_interaction.created_at


def get_network_status(session):
    last_network_location = session.query(db.Network).order_by(db.Network.created_at.desc()).first()
    return last_network_location
