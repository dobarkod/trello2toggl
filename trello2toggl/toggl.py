import requests
import json

from .jsonobject import JSONObject


class Toggl(object):
    """Simple Toggl API (v8) wrapper"""

    BASE_URL = 'https://www.toggl.com/api/v8/'

    def __init__(self, api_token):
        """Initialize the wrapper with the provided API token."""
        self.api_token = api_token

    def _get(self, endpoint):
        resp = requests.get(self.BASE_URL + endpoint,
            auth=(self.api_token, 'api_token'))
        if resp.status_code != 200:
            raise Exception('Status code is %d' % resp.status_code)
        return resp.json()

    def _post(self, endpoint, data):
        resp = requests.post(self.BASE_URL + endpoint,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data),
            auth=(self.api_token, 'api_token'))
        if resp.status_code != 200:
            raise Exception('Status code is %d' % resp.status_code)
        return resp.json()

    def _put(self, endpoint, data):
        resp = requests.put(self.BASE_URL + endpoint,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data),
            auth=(self.api_token, 'api_token'))
        if resp.status_code != 200:
            raise Exception('Status code is %d' % resp.status_code)
        return resp.json()

    def _delete(self, endpoint):
        resp = requests.delete(self.BASE_URL + endpoint)
        if resp.status_code != 200:
            print endpoint, repr(resp.text)
            raise Exception('Status code is %d' % resp.status_code)
        return True

    def get_clients(self):
        return JSONObject.parse(self._get('clients'))

    def get_workspaces(self):
        return JSONObject.parse(self._get('workspaces'))

    def get_workspace_projects(self, wid):
        return JSONObject.parse(self._get('workspaces/%d/projects' % wid))

    def get_workspace_tasks(self, wid):
        return JSONObject.parse(self._get('workspaces/%d/tasks' % wid))

    def create_task(self, name, project_id, est=None):
        data = dict(name=name, pid=project_id)

        if est is not None:
            data['estimated_secods'] = est

        data = dict(task=data)
        return JSONObject.parse(self._post('tasks', data)['data'])

    def get_task(self, task_id):
        return JSONObject.parse(self._get('tasks/%d' % task_id)['data'])

    def destroy_task(self, task_id):
        return self._delete('tasks/%d' % task_id)

    def mark_task_done(self, task_id):
        task = self._get('tasks/%d' % task_id)['data']
        task['active'] = False
        new_data = dict(task=task)

        return JSONObject.parse(self._put('tasks/%d' % task_id,
            new_data)['data'])
