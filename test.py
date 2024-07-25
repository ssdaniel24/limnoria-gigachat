from supybot.test import *


class GigaChatTestCase(PluginTestCase):
    plugins = ('GigaChat',)

    def testMsg(self):
        self.assertNotError('msg Ты ведь нейросеть? Это так?')


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
