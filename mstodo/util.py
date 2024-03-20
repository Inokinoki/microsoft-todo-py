import logging

from datetime import date, datetime, timedelta
from dateutil import tz
from mstodo import __githubslug__, __version__


SYMBOLS = {
    'star': '★',
    'recurrence': '↻',
    'reminder': '⏰',
    'note': '✏️',
    'overdue_1x': '⚠️',
    'overdue_2x': '❗️'
}


def parsedatetime_calendar():
    from parsedatetime import Calendar, VERSION_CONTEXT_STYLE

    return Calendar(parsedatetime_constants(), version=VERSION_CONTEXT_STYLE)


def parsedatetime_constants():
    from parsedatetime import Constants
    from mstodo.models.preferences import Preferences

    loc = Preferences.current_prefs().date_locale or user_locale()

    return Constants(loc)


def user_locale():
    import locale

    loc = locale.getlocale(locale.LC_TIME)[0]

    if not loc:
        # In case the LC_* environment variables are misconfigured, catch
        # an exception that may be thrown
        try:
            loc = locale.getdefaultlocale()[0]
        except IndexError:
            loc = 'en_US'

    return loc


def format_time(time, fmt):
    cnst = parsedatetime_constants()

    expr = cnst.locale.timeFormats[fmt]
    expr = (expr
            .replace('HH', '%H')
            .replace('h', '%I')
            .replace('mm', '%M')
            .replace('ss', '%S')
            .replace('a', '%p')
            .replace('z', '%Z')
            .replace('v', '%z'))

    return time.strftime(expr).lstrip('0')


def short_relative_formatted_date(dt):
    dt_date = dt.date() if isinstance(dt, datetime) else dt
    today = date.today()
    # Mar 3, 2016. Note this is a naive date in local TZ
    date_format = '%b %d, %Y'

    if dt_date == today:
        return 'today'
    if dt_date == today + timedelta(days=1):
        return 'tomorrow'
    if dt_date == today - timedelta(days=1):
        return 'yesterday'
    if dt_date.year == today.year:
        # Wed, Mar 3
        date_format = '%a, %b %d'

    return dt.strftime(date_format)


def utc_to_local(utc_dt):
    import calendar

    # get integer timestamp to avoid precision lost. Returns naive local datetime
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    return local_dt.replace(microsecond=utc_dt.microsecond)


def _report_errors(fn):
    def report_errors(*args, **kwargs):
        response = fn(*args, **kwargs)
        if response.status_code > 500:
            response.raise_for_status()
        return response
    return report_errors


def set_due_date(due_date):
    due_date = datetime.datetime.combine(due_date, datetime.time(0, 0, 0, 1))
    # Microsoft ignores the time component of the API response so we don't do TZ conversion here
    return {
        'dueDateTime': {
            "dateTime": due_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z',
            "timeZone": "UTC"
        }
    }


def set_reminder_date(reminder_date):
    reminder_date = reminder_date.replace(tzinfo=tz.gettz())
    return {
        'isReminderOn': True,
        'reminderDateTime': {
            "dateTime": reminder_date.astimezone(tz.tzutc()) \
                .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z',
            "timeZone": "UTC"
        }
    }


def set_recurrence(recurrence_count, recurrence_type, due_date):
    recurrence = {'pattern':{},'range':{}}
    if recurrence_type == 'day':
        recurrence_type = 'daily'
    elif recurrence_type == 'week':
        recurrence_type = 'weekly'
        recurrence['pattern']['firstDayOfWeek'] = 'sunday'
        recurrence['pattern']['daysOfWeek'] = [due_date.strftime('%A')]
    elif recurrence_type == 'month':
        recurrence_type = 'absoluteMonthly'
        recurrence['pattern']['dayOfMonth'] = due_date.strftime('%d')
    elif recurrence_type == 'year':
        recurrence_type = 'absoluteYearly'
        recurrence['pattern']['dayOfMonth'] = due_date.strftime('%d')
        recurrence['pattern']['month'] = due_date.strftime('%m')
    recurrence['pattern']['interval'] = recurrence_count
    recurrence['pattern']['type'] = recurrence_type
    recurrence['range'] = {
        # "endDate": "String (timestamp)", only for endDate types
        # "numberOfOccurrences": 1024,
        # "recurrenceTimeZone": "string",
        'startDate': due_date.strftime('%Y-%m-%d'),
        'type': 'noEnd' # "endDate / noEnd / numbered"
    }
    return recurrence
