from . import controllers
from . import models
from . import hooks  # This will automatically execute hooks/__init__.py
from .hooks.create_store_accounts import post_init_hook