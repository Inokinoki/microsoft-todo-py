import msal

from mstodo import constant

class MSToDo:
    def __init__(self, app_name=constant.APP_TITLE, app_version=constant.APP_VERSION):
        # Set up msal application for this session
        self._token_cache = msal.SerializableTokenCache()
        self._app = msal.PublicClientApplication(
            client_id=constant.MS_AZURE_CLIENT_ID,
            token_cache=self._token_cache,
            app_name=app_name,
            app_version=app_version,
        )

        # Setup caches for tasks
        self._task_folders_cache = []
        self._tasks_cache = []
