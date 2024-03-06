import re

from mstodo.models.base import BaseModel

_hashtag_pattern = re.compile(r'(?<=\s)#\S+', re.UNICODE)

# Remove any non-word characters at the end of the hashtag
_hashtag_trim_pattern = re.compile(r'\W+$', re.UNICODE)

class Hashtag(BaseModel):
    """
    Extends the Base class and refines it for the Hashtag data structure 
    """

    @classmethod
    def sync(cls):
        from mstodo.models.task import Task

        tasks_with_hashtags = Task.select().where(Task.title.contains('#'))
        hashtags = {}

        for task in tasks_with_hashtags:
            for hashtag in cls.hashtags_in_task(task):
                tag = re.sub(_hashtag_trim_pattern, r'', hashtag)
                hashtags[tag.lower()] = tag

        if len(hashtags) > 0:
            hashtag_data = [{'id': id, 'tag': tag, 'revision': 0} for (id, tag) in hashtags.items()]
            instances = cls.select()

            return cls._perform_updates(instances, hashtag_data)

        return False

    @classmethod
    def hashtags_in_task(cls, task):
        return set(re.findall(_hashtag_pattern, ' ' + task.title))
