from supybot.test import *
import supybot.conf as conf
from unittest.mock import patch

from gigachat.models import (ChatCompletion, Choices, Messages, MessagesRole,
                             Usage)


# taken from https://github.com/ai-forever/langchain-gigachat/blob/c2dc5bb8edd693ee185b7685841a39dabfad621f/libs/gigachat/tests/unit_tests/test_gigachat.py#L40-L54
gigachat_response = ChatCompletion(
    choices=[Choices(message=Messages(id=None, role=MessagesRole.ASSISTANT,
                                       content="Bar Baz"),
                     index=0,
                     finish_reason="stop",)],
    created=1678878333,
    model="GigaChat:v1.2.19.2",
    usage=Usage(prompt_tokens=18, completion_tokens=68, total_tokens=86),
    object="chat.completion",
)

class GigaChatTestCase(PluginTestCase):
    plugins = ('GigaChat',)

    def test_msg_without_creds(self):
        self.assertError('msg Hey, who are you?')

    @patch('gigachat.GigaChat.chat', return_value=gigachat_response)
    def test_msg(self, mock):
        with conf.supybot.plugins.GigaChat.auth_creds.context('AuTh_CrEdS123'):
            self.assertResponse('msg say something', 'Bar Baz')


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
