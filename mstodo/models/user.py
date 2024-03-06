import logging
import time

from mstodo.models.base import BaseModel

log = logging.getLogger(__name__)

class User(BaseModel):
    """
    Extends the Base class and refines it for the User data structure 
    """

    @classmethod
    def sync(cls):
        from mstodo.api import user

        start = time.time()
        instance = None
        user_data = user.user()
        log.debug(f"Retrieved User in {round(time.time() - start, 3)}")

        try:
            instance = cls.get()
        except User.DoesNotExist:
            pass

        return cls._perform_updates([instance], [user_data])
