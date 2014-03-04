import threading
from collections import defaultdict

thread_local = threading.local()
thread_local.models = dict()

def set_view(view):
    thread_local.view = view

def get_view():
    return getattr(thread_local, 'view', None)

def add_model(model):
    thread_local.models[model.__name__] = model

def get_model(name):
    return thread_local.models[name]

from . import utils
from . import generators

from .utils import run_pipeline
