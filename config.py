from supybot import conf, registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('GigaChat')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified themself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('GigaChat', True)


GigaChat = conf.registerPlugin('GigaChat')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(GigaChat, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))
conf.registerGlobalValue(GigaChat, 'auth_creds',
        registry.String('', _("""Your GigaChat autorization data (required)."""),
        private=True))

conf.registerGlobalValue(GigaChat, 'verify_ssl_serts',
        registry.Boolean(False, _("""Verify GigaChat API certs or not"""),
        private=True))

conf.registerGlobalValue(GigaChat, 'new_line_symbol',
        registry.StringSurroundedBySpaces(' ↵ ', _("""Symbol (or string), which
        will be used instead of newline (\\n) in GigaChat answers.""")))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
