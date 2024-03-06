import mstodo

MS_AZURE_CLIENT_ID = "27f3e5af-2d84-4073-91fa-9390208d1527"
MS_TODO_SCOPE =  [
    "User.Read",
    "Tasks.ReadWrite",
    "Tasks.ReadWrite.Shared",
    "MailboxSettings.ReadWrite"
]
MS_TODO_API_BASE_URL =  "https://graph.microsoft.com/beta"
MS_TODO_PAGE_SIZE = '1000'
APP_TITLE = mstodo.__title__
APP_VERSION = mstodo.__version__
