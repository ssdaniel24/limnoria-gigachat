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


import gigachat


class GigaChat(callbacks.Plugin):
    """Implements GigaChat AI API."""
    threaded = True

    @wrap(['text'])
    def chat(self, irc, msg, args, text):
        """<message>

        Sends the <message> to the GigaChat AI and prints answer.
        """
        creds = self.registryValue('auth_creds')
        if creds == '':
            irc.error(_('"auth_creds" config value is empty!'))
            print(creds)
            return

        giga = gigachat.GigaChat(credentials=creds, verify_ssl_certs=self.registryValue('verify_ssl_serts'))
        response = giga.chat(text)
        raw_reply = response.choices[0].message.content
        reply = ' '.join(raw_reply.splitlines())
        irc.reply(reply)


Class = GigaChat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
