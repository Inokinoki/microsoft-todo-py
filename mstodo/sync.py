import os
import time
import logging
from datetime import datetime

from mstodo.util import wf_wrapper

log = logging.getLogger(__name__)
wf = wf_wrapper()

def sync(background=False):
    from mstodo.models import base, task, user, taskfolder, hashtag
    from peewee import OperationalError

    # If a sync is already running, wait for it to finish. Otherwise, store
    # the current pid in alfred-workflow's pid cache file
    if not background:
        log.info("Running manual sync")

        pidfile = wf.cachefile('sync.pid')
        with open(pidfile, 'w', encoding="utf-8") as file_obj:
            #@TODO check if this needs to be byte-written? May be due to pickling the program state?
            # file_obj.write(os.getpid().to_bytes(length=4, byteorder=sys.byteorder))
            file_obj.write(str(os.getpid()))
    else:
        log.info('Running background sync')


    base.BaseModel._meta.database.create_tables([
        taskfolder.TaskFolder,
        task.Task,
        user.User,
        hashtag.Hashtag
    ], safe=True)

    # Perform a query that requires the latest schema; if it fails due to a
    # mismatched scheme, delete the old database and re-sync
    try:
        task.Task.select().where(task.Task.recurrence_count > 0).count()
        hashtag.Hashtag.select().where(hashtag.Hashtag.tag == '').count()
    except OperationalError:
        base.BaseModel._meta.database.close()
        wf.clear_data(lambda f: 'mstodo.db' in f)

        # Make sure that this sync does not try to wait until its own process
        # finishes
        sync(background=True)
        return

    first_sync = False

    try:
        # get root item from DB. If it doesn't exist then make this the first sync.
        user.User.get()
    except user.User.DoesNotExist:
        first_sync = True
        wf.cache_data('last_sync',datetime.utcnow())

    user.User.sync()
    taskfolder.TaskFolder.sync()
    if first_sync:
        task.Task.sync_all_tasks()
    else:
        task.Task.sync_modified_tasks()
    hashtag.Hashtag.sync()
    #@TODO move this into a child sync of the relevant tasks once bugfix is completed

    sync_completion_time = datetime.utcnow()

    if first_sync or not background:
        log.info(f"Sync completed at {sync_completion_time}")

    wf.cache_data('last_sync',sync_completion_time)
    log.debug(f"This sync time: {sync_completion_time}")
    return True
