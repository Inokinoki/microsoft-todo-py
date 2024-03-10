from mstodo import constant

class MSToDo:
    def __init__(self, base_url=constant.MS_TODO_API_BASE_URL, page_size=1000):
        # Set up request configs
        self._base_url = base_url
        self._page_size = page_size

        # Setup caches for tasks
        self._task_folders_cache = []
        self._tasks_cache = []
