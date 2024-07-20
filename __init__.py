"""
GigaChat: Implements GigaChat AI API.
"""

import sys
import supybot
from supybot import world


__version__ = "0.1"
__author__ = supybot.Author(nick='ssdaniel24', email='bo7oaonteg2m@mail.ru')
__contributors__ = {}
__url__ = 'https://github.com/ssdaniel24/limnoria-gigachat'

from . import config
from . import plugin
from importlib import reload
# In case we're being reloaded.
reload(config)
reload(plugin)
# Add more reloads here if you add third-party modules and want them to be
# reloaded when this plugin is reloaded.  Don't forget to import them as well!

if world.testing:
    from . import test

Class = plugin.Class
configure = config.configure


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
