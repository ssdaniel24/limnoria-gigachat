from supybot import conf, ircdb, callbacks
from supybot.commands import *

from supybot.i18n import PluginInternationalization, internationalizeDocstring
_ = PluginInternationalization('GigaChat')


import os, sqlite3
from time import time_ns
from uuid import uuid1
from gigachat import GigaChat as GC
from gigachat.models import Chat, Messages, MessagesRole


class GigachatDB:
    """Abstraction over low-level DB functions"""
    def __init__(self, filename: str):
        does_database_exist = os.path.exists(filename)
        self._connection = sqlite3.connect(filename, check_same_thread=False)
        if not does_database_exist:
            self._create()

    def _create(self):
        """Creates database tables from scratch"""
        cur = self._connection.cursor()
        cur.execute("""
            CREATE TABLE Prompts(prompt_id BLOB NOT NULL PRIMARY KEY,
                                 name TEXT,
                                 created_at INTEGER NOT NULL,
                                 content TEXT,
                                 user_id INTEGER REFERENCES UserCurrent,
                                 UNIQUE(name, user_id));
        """)
        cur.execute("""
            CREATE TABLE Chats(chat_id BLOB NOT NULL PRIMARY KEY,
                               name TEXT,
                               prompt_id BLOB REFERENCES Prompts,
                               user_id INTEGER REFERENCES UserCurrent,
                               UNIQUE(name, user_id));
        """)
        cur.execute("""
            CREATE TABLE Messages(message_id BLOB NOT NULL PRIMARY KEY,
                                  role INTEGER CHECK (role IN (1, 2)),
                                  created_at INTEGER NOT NULL,
                                  content TEXT,
                                  chat_id BLOB REFERENCES Chats);
        """)
        cur.execute("""
            CREATE TABLE UserCurrent(user_id INTEGER NOT NULL PRIMARY KEY,
                                     chat_id BLOB REFERENCES Chats,
                                     prompt_id BLOB REFERENCES Prompts);
        """)
        self._connection.commit()

    def _get_timestamp(self) -> int:
        return time_ns()

    def get_messages(self, user_id: int) -> list[Messages]:
        """Gets messages from DB and returns list of Messages objects that can
        be used in Gigachat queries"""
        cur = self._connection.cursor()
        chat_id = self._get_current_user_chat(user_id)
        cur.execute("""
            SELECT role, content FROM Messages
                WHERE chat_id = ?
                ORDER BY created_at;
        """, (chat_id,))
        messages = []
        for (role, content) in cur.fetchall():
            role = MessagesRole.USER if role == 1 else MessagesRole.ASSISTANT
            messages.append(Messages(role=role, content=content))
        return messages

    def _get_current_user_chat(self, user_id: int) -> bytes:
        """Returns current user chat id (bytes). Creates default chat if user
        is new."""
        cur = self._connection.cursor()
        cur.execute("""
            SELECT chat_id FROM Chats
                WHERE user_id = ?;
        """, (user_id,))
        res = cur.fetchone()
        if res is not None:
            return res[0]
        return self.create_chat(user_id, 'default')

    def does_chat_exist(self, user_id: int, chat_name: str) -> bool:
        """Checks if user have chat with given name"""
        cur = self._connection.cursor()
        cur.execute("""
            SELECT chat_id FROM Chats
                WHERE user_id = ? AND
                      name = ?;
        """, (user_id, chat_name))
        res = cur.fetchone()
        return res is not None

    def create_chat(self, user_id: int, chat_name: str) -> bytes:
        """Creates user chat with given name. Returns chat id in bytes."""
        cur = self._connection.cursor()
        chat_id = uuid1().bytes
        row = (chat_id, chat_name, None, user_id)
        cur.execute("""INSERT INTO Chats VALUES(?, ?, ?, ?)""", row)
        return chat_id

    def change_current_chat(self, user_id: int, chat_name: str):
        cur = self._connection.cursor()
        cur.execute("""
            UPDATE UserCurrent
                SET chat_id =
                    (SELECT chat_id FROM Chats
                        WHERE user_id = ? AND
                              chat_name = ?)
                WHERE user_id = ?;
        """, (user_id, chat_name, user_id))

    def add_message(self, user_id: int, message: Messages):
        """Adds given message to user conservation in DB"""
        cur = self._connection.cursor()
        chat_id = self._get_current_user_chat(user_id)
        role = message.role
        role_in_db = 1 if role == MessagesRole.USER else 2 # MessagesRole.ASSISTANT
        row = (uuid1().bytes, role_in_db, self._get_timestamp(),
               message.content, chat_id)
        cur.execute("""INSERT INTO Messages VALUES(?, ?, ?, ?, ?)""", row)

    def rm_last_bot_message(self, user_id: int):
        """Removes last bot message from given user chat"""
        cur = self._connection.cursor()
        chat_id = self._get_current_user_chat(user_id)
        cur.execute("""
            DELETE FROM Messages
                WHERE message_id =
                    (SELECT message_id FROM Messages
                        WHERE chat_id = ? AND role = 2
                        ORDER BY created_at
                        LIMIT 1);
        """, (chat_id,))

    def clear_chat(self, user_id: int):
        """Deletes every message from given user's chat with given name"""
        cur = self._connection.cursor()
        chat_id = self._get_current_user_chat(user_id)
        cur.execute("""DELETE FROM Messages WHERE chat_id = ?;""", (chat_id,))

    def close(self):
        self._connection.close()


class GigaChat(callbacks.Plugin):
    """Implements GigaChat AI API."""
    # threaded = True
    def __init__(self, irc):
        self.__parent = super(GigaChat, self)
        self.__parent.__init__(irc)
        self.db = GigachatDB(os.path.join(conf.supybot.directories.data(),
                'GigaChat.db'))

    def _replace_new_lines(self, text: str) -> str:
        text = text.replace('\n\n', '\n')
        text = text.replace('\n', self.registryValue('new_line_symbol'))
        return text

    def is_config_ok(self, irc) -> bool:
        """Checks config for need values and returns False, if they are not
        set. Also sends error to user via given irc context."""
        if not self.registryValue('enabled'):
            irc.error(_('Plugin is turned off in this channel'))
            return False
        if self.registryValue('auth_creds') == '':
            irc.error(_('"auth_creds" config value is empty!'))
            return False
        return True

    def get_answer(self, channel, messages: list[Messages]) -> Messages:
        """Returns answer from AI"""
        creds = self.registryValue('auth_creds')
        giga = GC(credentials=creds,
                verify_ssl_certs=self.registryValue('verify_ssl_certs'))

        resp = giga.chat(Chat(
            model=self.registryValue("model", channel),
            messages=messages,
            max_tokens=self.registryValue('max_tokens', channel),
        ))
        return resp.choices[0].message

    @internationalizeDocstring
    def msg(self, irc, msg, args, text):
        """<message>

        Sends the <message> to the GigaChat AI and prints answer.
        """
        if not self.is_config_ok(irc):
            return

        prompt = self.registryValue("prompt", msg.channel).replace('$botnick',
                irc.nick)

        raw_reply = self.get_answer(msg.channel, messages=[
            Messages(role=MessagesRole.SYSTEM, content=prompt),
            Messages(role=MessagesRole.USER, content=text),
        ]).content
        reply = self._replace_new_lines(raw_reply)
        irc.reply(reply)
    msg = wrap(msg, ['text'])

    @internationalizeDocstring
    def amsg(self, irc, msg, args, text):
        """<message>

        Sends the <message> to the GigaChat AI, prints answer and saves it in
        DB for using in future answers.
        """
        if not self.is_config_ok(irc):
            return

        try:
            user_id = ircdb.users.getUser(msg.prefix).id
        except KeyError:
            irc.errorNotRegistered()
            return

        prompt = self.registryValue("prompt", msg.channel).replace('$botnick',
                irc.nick)

        messages = self.db.get_messages(user_id)
        messages.insert(0, Messages(role=MessagesRole.SYSTEM, content=prompt))
        user_message = Messages(role=MessagesRole.USER, content=text)
        messages.append(user_message)
        print(messages)

        ai_answer = self.get_answer(msg.channel, messages=messages)
        self.db.add_message(user_id, user_message)
        self.db.add_message(user_id, ai_answer)
        reply = self._replace_new_lines(ai_answer.content)
        irc.reply(reply)
    amsg = wrap(amsg, ['text'])

    @internationalizeDocstring
    def retry(self, irc, msg, args):
        """takes no arguments

        Deletes last AI message from current chat and gets new AI answer.
        """
        if not self.is_config_ok(irc):
            return

        try:
            user_id = ircdb.users.getUser(msg.prefix).id
        except KeyError:
            irc.errorNotRegistered()
            return

        prompt = self.registryValue("prompt", msg.channel).replace('$botnick',
                irc.nick)

        self.db.rm_last_bot_message(user_id)
        messages = self.db.get_messages(user_id)
        messages.insert(0, Messages(role=MessagesRole.SYSTEM, content=prompt))
        print(messages)

        ai_answer = self.get_answer(msg.channel, messages=messages)
        self.db.add_message(user_id, ai_answer)
        reply = self._replace_new_lines(ai_answer.content)
        irc.reply(reply)
    retry = wrap(retry)

    @internationalizeDocstring
    def clear(self, irc, msg, args):
        """takes no arguments

        Clears your conservation with Gigachat AI, so you will start chat from
        scratch without any context.
        """
        if not self.is_config_ok(irc):
            return

        try:
            user_id = ircdb.users.getUser(msg.prefix).id
        except KeyError:
            irc.errorNotRegistered()
            return

        self.db.clear_chat(user_id)
        irc.replySuccess()
    clear = wrap(clear)

    def die(self):
        self.db.close()
        self.__parent.die()

Class = GigaChat


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
