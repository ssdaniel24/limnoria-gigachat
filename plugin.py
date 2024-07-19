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


from gigachat import GigaChat as GC
from gigachat.models import Chat, Messages, MessagesRole


class GigaChat(callbacks.Plugin):
    """Implements GigaChat AI API."""
    threaded = True

    improvised_db: dict[str, list[Messages]] = {}

    def _replace_new_lines(self, text: str) -> str:
        text = text.replace('\n\n', '\n')
        text = text.replace('\n', self.registryValue('new_line_symbol'))
        return text

    @wrap([
        getopts({
            'max-tokens': 'positiveInt',
        }),
        'text',
    ])
    def msg(self, irc, msg, args, optlist, text):
        """[--max-tokens <positive int>] <message>

        Sends the <message> to the GigaChat AI and prints answer. You can
        configure max tokens number that will be used for answer.
        """
        creds = self.registryValue('auth_creds')
        if creds == '':
            irc.error(_('"auth_creds" config value is empty!'))
            return

        max_tokens = None
        for (opt, arg) in optlist:
            if opt == 'max-tokens':
                max_tokens = arg

        giga = GC(credentials=creds,
                        verify_ssl_certs=self.registryValue('verify_ssl_serts'))
        resp = giga.chat(Chat(
            messages=[Messages(
                role=MessagesRole.USER,
                content=text,
            )],
            max_tokens=max_tokens
        ))
        raw_reply = resp.choices[0].message.content
        reply = self._replace_new_lines(raw_reply)
        irc.reply(reply)


    @wrap([
        getopts({
            'max-tokens': 'positiveInt',
            'restore': '',
        }),
        'text',
    ])
    def chat(self, irc, msg, args, optlist, text):
        """[--max-tokens <positive int>] [--restore] <message>

        Same as 'msg' command, but it saves all conservation messages per user.
        The '--restore' flag will purge saved messages, so you will start
        conservation from scratch.
        """
        creds = self.registryValue('auth_creds')
        if creds == '':
            irc.error(_('"auth_creds" config value is empty!'))
            return

        max_tokens = None
        to_restore = False
        for (opt, arg) in optlist:
            if opt == 'max-tokens':
                max_tokens = arg
            if opt == 'restore':
                to_restore = True

        giga = GC(credentials=creds,
                        verify_ssl_certs=self.registryValue('verify_ssl_serts'))

        messages = self.improvised_db.get(msg.nick) or []
        if to_restore:
            messages = []
        messages.append(Messages(
            role=MessagesRole.USER,
            content=text,
        ))
        resp = giga.chat(Chat(
            messages=messages,
            max_tokens=max_tokens
        ))
        raw_reply = resp.choices[0].message.content
        reply = self._replace_new_lines(raw_reply)
        irc.reply(reply)
        messages.append(resp.choices[0].message)
        self.improvised_db[msg.nick] = messages



Class = GigaChat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
