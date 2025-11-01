# Compatibility shim: keep old import path `config.settings` working
# after moving the real settings to `database.config.settings`.
from database.config.settings import *
