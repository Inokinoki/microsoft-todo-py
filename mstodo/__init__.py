__version__ = '0.2.2'
__author__ = 'Johan de Beurs, Ian Paterson, Inoki'
__licence__ = 'MIT'
__copyright__ = 'Copyright 2024 Inoki, Copyright 2023 Johan de Beurs, 2013-2017 Ian Paterson'
__githubslug__ = 'Inokinoki/microsoft-todo-py'

def get_version():
    return __version__

def get_github_slug():
    return __githubslug__

from mstodo.mstodo import MSToDo
