import json
from requests import codes
import requests
import time

from mstodo import constant

import logging

logger = logging.getLogger(__name__)


class MSToDo:
    def __init__(self, base_url=constant.MS_TODO_API_BASE_URL, page_size=1000):
        # Set up request configs
        self._base_url = base_url
        self._page_size = page_size

        # Setup caches for tasks
        self._task_folders_cache = []
        self._tasks_cache = []

        self._token = None
        self._session = requests.Session(base_url=self._base_url)
        self._session.headers['Content-Type'] = 'application/json'
        if self._token:
            self._session.headers['Authorization'] = f"Bearer {self._token}"

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

    def taskfolders(self, order='display', task_counts=False):
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

    def taskfolder(self, _id, task_counts=False):
        res = self._session.get(f"me/outlook/taskFolders/{_id}")
        info = res.json()

        if task_counts:
            self.update_taskfolder_with_tasks_count(info)

        return info

    def taskfolder_tasks_count(self, _id):
        info = {}
        req = self._get(f"taskFolders/{_id}/tasks?$count=true&$top=1&$filter=status+ne+'completed'")
        info['uncompleted_count'] = req.json()['@odata.count']
        req = self._get(f"taskFolders/{_id}/tasks?$count=true&$top=1&$filter=status+eq+'completed'")
        info['completed_count'] = req.json()['@odata.count']

        return info

    def update_taskfolder_with_tasks_count(self, info):
        counts = self.taskfolder_tasks_count(info['id'])
        info['completed_count'] = counts.get('completed_count', 0)
        info['uncompleted_count'] = counts.get('uncompleted_count', 0)
        return info

    def create_taskfolder(self, title):
        req = self._post('me/outlook/taskFolders', {'name': title})
        return req

    def delete_taskfolder(self, _id):
        req = self._delete('me/outlook/taskFolders/' + _id)
        return req.status_code == codes.no_content

    # Other methods can be added similarly
    def user(self):
        req = self._get('me')
        return req.json()
