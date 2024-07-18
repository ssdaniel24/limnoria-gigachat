from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
from supybot.i18n import PluginInternationalization


try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('GigaChat')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class GigaChat(callbacks.Plugin):
    """Implements GigaChat AI API."""
    threaded = True


Class = GigaChat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
