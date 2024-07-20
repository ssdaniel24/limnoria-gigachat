from supybot import utils, plugins, ircutils, callbacks
from supybot.commands import *
from supybot.i18n import PluginInternationalization

from supybot.i18n import PluginInternationalization, internationalizeDocstring
_ = PluginInternationalization('GigaChat')


from gigachat import GigaChat as GC
from gigachat.models import Chat, Messages, MessagesRole


class GigaChat(callbacks.Plugin):
    """Implements GigaChat AI API."""
    threaded = True

    def _replace_new_lines(self, text: str) -> str:
        text = text.replace('\n\n', '\n')
        text = text.replace('\n', self.registryValue('new_line_symbol'))
        return text

    @wrap(['text'])
    @internationalizeDocstring
    def msg(self, irc, msg, args, text):
        """<message>

        Sends the <message> to the GigaChat AI and prints answer. You can
        configure max tokens number that will be used for answer.
        """
        creds = self.registryValue('auth_creds')
        if creds == '':
            irc.error(_('"auth_creds" config value is empty!'))
            return

        giga = GC(credentials=creds,
                verify_ssl_certs=self.registryValue('verify_ssl_certs'))

        prompt = self.registryValue("prompt", msg.channel).replace('$botnick',
                irc.nick)

        resp = giga.chat(Chat(
            model=self.registryValue("model", msg.channel),
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=prompt),
                Messages(role=MessagesRole.USER, content=text)
            ],
            max_tokens=self.registryValue('max_tokens', msg.channel),
        ))
        raw_reply = resp.choices[0].message.content
        reply = self._replace_new_lines(raw_reply)
        irc.reply(reply)


Class = GigaChat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
