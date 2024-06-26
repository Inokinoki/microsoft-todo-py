# encoding: utf-8
"""
Generated by `codellama/CodeLlama-70b-Instruct-hf`
Prompt: Help me to write a Pydantic model class, allowing converting this json to Python object:
{
    'id': '<task_id>',
    'createdDateTime': '2024-03-16T12:46:23.5138127Z',
    'lastModifiedDateTime': '2024-03-16T12:47:10.1670318Z',
    'changeKey': '<changekey>',
    'categories': [],
    'assignedTo': '',
    'hasAttachments': False,
    'importance': 'normal',
    'isReminderOn': False,
    'owner': 'Shaw Inoki',
    'parentFolderId': '<task_folder_id>',
    'sensitivity': 'normal',
    'status': 'notStarted',
    'subject': '<subject>',
    'body': {'contentType': 'html',
    'content': '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n<meta name="Generator" content="Microsoft Exchange Server">\r\n<!-- converted from text -->\r\n<style><!-- .EmailQuote { margin-left: 1pt; padding-left: 4pt; border-left: #800000 2px solid; } --></style></head>\r\n<body>\r\n<font size="2"><span style="font-size:11pt;"><div class="PlainText">&nbsp;</div></span></font>\r\n</body>\r\n</html>\r\n'},
    'completedDateTime': None,
    'dueDateTime': None,
    'recurrence': None,
    'reminderDateTime': None,
    'startDateTime': None
}
"""

from datetime import datetime
import logging

log = logging.getLogger(__name__)

_days_by_recurrence_type = {
    'day': 1,
    'week': 7,
    'month': 30.43,
    'year': 365
}

_primary_api_fields = [
    'id',
    'parentFolderId',
    'lastModifiedDateTime',
    'changeKey',
    'status'
]
_secondary_api_fields = [
    'createdDateTime',
    'startDateTime',
    'dueDateTime',
    'isReminderOn',
    'reminderDateTime',
    'completedDateTime',
    'recurrence',
    'subject',
    'body',
    'importance',
    'sensitivity',
    'hasAttachments',
    'owner',
    'assignedTo'
]

from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum
from uuid import UUID

# Importing `BaseModel` and other types from Pydantic library
from pydantic import BaseModel, Field, validator

class ContentType(str, Enum):
    html = "html"
    plain_text = "plain_text"


class Body(BaseModel):
    """Represents body of an item."""
    content_type: ContentType = Field(...)
    content: str = Field(...)


class Task(BaseModel):
    id: UUID = Field(...)                                # Unique identifier (UUID) type
    created_date_time: datetime = Field(...)             # Datetime field representing creation timestamp
    last_modified_datetime: datetime = Field(...)        # Datetime field representing modification timestamp
    change_key: str = Field(...)                         # Change key string value
    categories: List[str] = Field([])                    # Categories as empty list by default
    assigned_to: str = Field('')                         
    has_attachments: bool = Field(False)                 # Boolean flag indicating whether attachments exist or not
    importance: str = Field("normal")                    # String denoting task importance level ('low', 'medium', 'high')
    is_reminder_on: bool = Field(False)                  # Reminder on/off boolean flag
    owner: str = Field('')                               # Owner name
    parent_folder_id: UUID = Field(...)                  # Parent folder unique ID
    sensitivity: str = Field("normal")                   # Sensitivity level ('normal', 'private', 'confidential')
    status: str = Field("notStarted")                    # Status of the task ('notStarted', 'inProgress', 'completed', 'waitingOnOthers', 'deferred')
    subject: str = Field('')                             
    body: Body = Field({})                               # Empty body by default
    completed_date_time: Optional[datetime] = None       # Completion datetime if present, otherwise set to None
    due_date_time: Optional[datetime] = None             # Due datetime if specified, otherwise set to None
    recurrence: Optional[dict] = None                    # Recurring pattern dictionary if applicable, else set to None
    reminder_date_time: Optional[datetime] = None        # Reminder datetime if enabled, otherwise set to None
    start_date_time: Optional[datetime] = None           # Start datetime if defined, otherwise set to None

    @validator("*", pre=True)
    def parse_timestamps(cls, v):
        """Custom validator function to convert ISO timestamps into datetime objects."""
        if isinstance(v, str) and v.endswith("Z"):
            return datetime.fromisoformat(v[:-1])
        return v
