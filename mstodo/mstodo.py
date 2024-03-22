import datetime
from dateutil import tz
import json
from requests import codes
from requests_toolbelt import sessions
import time

from mstodo import constant
from mstodo.util import set_due_date, set_reminder_date, set_recurrence
from mstodo.models import Task, TaskFolder

import logging

logger = logging.getLogger(__name__)


class MSToDo:
    def __init__(self, base_url=constant.MS_TODO_API_BASE_URL, token=None, page_size=1000):
        # Set up request configs
        self._base_url = base_url
        self._page_size = page_size

        # Setup caches for tasks
        self._task_folders_cache = []
        self._tasks_cache = []

        self._token = token
        self._session = sessions.BaseUrlSession(base_url=base_url)
        self._session.headers['Content-Type'] = 'application/json'
        self.auth(self._token)

    def _get(self, path, params=None):
        return self._session.get(path, params=params)
    
    def _post(self, path, data=None):
        return self._session.post(path, data=json.dumps(data))

    def _put(self, path, data=None):
        return self._session.put(path, data=json.dumps(data))

    def _patch(self, path, data=None):
        return self._session.patch(path, data=json.dumps(data))

    def _delete(self, path, data=None):
        return self._session.delete(path, data=json.dumps(data))

    def _build_querystring(self, completed=None, dt=None, afterdt=True, fields=None):
        if fields is None:
            fields = []
        query = f"?$top={self._page_size}&count=true&$select={''.join([field + ',' for field in fields])[:-1]}"
        if (completed is not None or dt is not None):
            query += '&$filter='
            if completed is True:
                query += "status+eq+'completed'"
            elif completed is False:
                query += "status+ne+'completed'"
            if completed is not None:
                query += "&"
            if dt is not None:
                query += f"lastModifiedDateTime+{'ge+' if afterdt else 'lt+'}{dt.isoformat()[:-4]}Z"
        else:
            query += ''
        return query

    def taskfolders_raw(self, order='display', task_counts=False):
        start = time.time()
        query = f"?$top={self._page_size}&count=true"
        next_link = f"me/outlook/taskFolders{query}"
        taskfolders = []
        while True:
            req = self._get(next_link)
            taskfolders.extend(req.json()['value'])
            if '@odata.nextLink' in req.json():
                next_link = req.json()['@odata.nextLink'].replace(self._base_url + '/','')
            else:
                logger.debug(f"Retrieved taskFolders in {round(time.time() - start, 3)} seconds")
                break

        if task_counts:
            for taskfolder in taskfolders:
                self.update_taskfolder_with_tasks_count(taskfolder)

        return taskfolders

    def taskfolder_raw(self, _id, task_counts=False):
        res = self._session.get(f"me/outlook/taskFolders/{_id}")
        info = res.json()

        if task_counts:
            self.update_taskfolder_with_tasks_count(info)

        return info

    def create_taskfolder_raw(self, title):
        req = self._post('me/outlook/taskFolders', {'name': title})
        return req

    def delete_taskfolder_raw(self, _id):
        req = self._delete('me/outlook/taskFolders/' + _id)
        return req.status_code == codes.no_content

    def tasks_raw(self, taskfolder_id=None, completed=None, dt=None, afterdt=None, fields=None):
        if fields is None:
            fields = []
        if taskfolder_id is not None:
            root_uri = f"me/outlook/taskFolders/{taskfolder_id}/tasks"
        else:
            root_uri = "me/outlook/tasks"
        next_link = root_uri + self._build_querystring(
            completed=completed,
            dt=dt,
            afterdt=afterdt,
            fields=fields
        )
        task_data = []
        while True:
            start_page = time.time()
            req = self._get(next_link)
            task_data.extend(req.json()['value'])
            logger.debug(f"Retrieved {len(req.json()['value'])} {'modified ' if afterdt else ''}\
{'completed ' if completed else ''}tasks in {round(time.time() - start_page, 3)} seconds")
            if '@odata.nextLink' in req.json():
                next_link= req.json()['@odata.nextLink'].replace(f"{self._base_url}/",'')
            else:
                break

        return task_data

    def task_raw(self, task_id):
        req = self._get('me/outlook/tasks/' + task_id)
        info = req.json()

        return info

    def create_task_raw(self, taskfolder_id, title, assignee_id=None, recurrence_type=None,
                    recurrence_count=None, due_date=None, reminder_date=None,
                    starred=False, completed=False, note=None):
        params = {
            'subject': title,
            'importance': 'high' if starred else 'normal',
            'status': 'completed' if completed else 'notStarted',
            'sensitivity': 'normal',
            'isReminderOn': False,
            'body': {
                'contentType':'text',
                'content': note if note else ''
            }
        }
        if due_date:
            due_date = datetime.datetime.combine(due_date,datetime.time(0, 0, 0, 1))
            # Microsoft ignores the time component of the API response so we don't do TZ conversion here
            params['dueDateTime'] = {
                "dateTime": due_date.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z',
                "timeZone": "UTC"
            }
        if reminder_date:
            reminder_date = reminder_date.replace(tzinfo=tz.gettz())
            params['isReminderOn'] = True
            params['reminderDateTime'] = {
                "dateTime": reminder_date.astimezone(tz.tzutc()) \
                    .strftime('%Y-%m-%dT%H:%M:%S.%f')[:-4] + 'Z',
                "timeZone": "UTC"
            }
        if (recurrence_count is not None and recurrence_type is not None):
            params['recurrence'] = {'pattern':{},'range':{}}
            if recurrence_type == 'day':
                recurrence_type = 'daily'
            elif recurrence_type == 'week':
                recurrence_type = 'weekly'
                params['recurrence']['pattern']['firstDayOfWeek'] = 'sunday'
                params['recurrence']['pattern']['daysOfWeek'] = [due_date.strftime('%A')]
            elif recurrence_type == 'month':
                recurrence_type = 'absoluteMonthly'
                params['recurrence']['pattern']['dayOfMonth'] = due_date.strftime('%d')
            elif recurrence_type == 'year':
                recurrence_type = 'absoluteYearly'
                params['recurrence']['pattern']['dayOfMonth'] = due_date.strftime('%d')
                params['recurrence']['pattern']['month'] = due_date.strftime('%m')
            params['recurrence']['pattern']['interval'] = recurrence_count
            params['recurrence']['pattern']['type'] = recurrence_type
            params['recurrence']['range'] = {
                # "endDate": "String (timestamp)", only for endDate types
                # "numberOfOccurrences": 1024,
                # "recurrenceTimeZone": "string",
                'startDate': due_date.strftime('%Y-%m-%d'),
                'type': 'noEnd' # "endDate / noEnd / numbered"
            }

        #@TODO maybe add these if required
        # params_new = {
        #     "categories": ["String"],
        #     "startDateTime": {"@odata.type": "microsoft.graph.dateTimeTimeZone"},
        # }

        #@TODO check these and add back if needed
        # if assignee_id:
        #     params['assignedTo'] = int(assignee_id)

        req = self._post(f"me/outlook/taskFolders/{taskfolder_id}/tasks", params)
        logger.debug(req.status_code)

        return req

    def update_task_raw(self, task_id, revision, title=None, assignee_id=None, recurrence_type=None,
                    recurrence_count=None, due_date=None, reminder_date=None, starred=None,
                    completed=None):
        params = {}

        if not completed is None:
            if completed:
                res = self._post(f"me/outlook/tasks/{task_id}/complete")
                return res
            else:
                params['status'] = 'notStarted'
                params['completedDateTime'] = {}

        if title is not None:
            params['subject'] = title

        if starred is not None:
            if starred is True:
                params['importance'] = 'high'
            elif starred is False:
                params['importance'] = 'normal'

        if due_date is not None:
            params.update(set_due_date(due_date))

        if reminder_date is not None:
            params.update(set_reminder_date(reminder_date))

        #@TODO this requires all three to be set. Need to ensure due_date is pulled from task on calling this function
        if (recurrence_count is not None and recurrence_type is not None and due_date is not None):
            params.update(set_recurrence(recurrence_count, recurrence_type, due_date))
        #@TODO maybe add these if required
        # params_new = {
        #     "categories": ["String"],
        #     "startDateTime": {"@odata.type": "microsoft.graph.dateTimeTimeZone"},
        # }

        #@TODO check these and add back if needed
        # if assignee_id:
        #     params['assignedTo'] = int(assignee_id)
        # remove = []

        if params:
            res = self._patch(f"me/outlook/tasks/{task_id}", params)

            return res

        return None

    def delete_task_raw(self, task_id, revision):
        res = self._delete(f"me/outlook/tasks/{task_id}")
        return res

    # Other methods can be added similarly
    def user_raw(self):
        req = self._get('me')
        return req.json()

    def auth(self, token):
        self._token = token
        if self._token:
            self._session.headers['Authorization'] = f"Bearer {self._token}"
