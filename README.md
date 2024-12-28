# Gigachat AI plugin for Limnoria

[Limnoria](https://limnoria.net/) is IRC bot and this repo is an implementation of [Gigachat](https://developers.sber.ru/gigachat) API. Inspired by [ChatGPT limnoria plugin by oddluck](https://github.com/oddluck/limnoria-plugins/tree/master/ChatGPT).

Requires [gigachat](https://github.com/ai-forever/gigachat) module.

TODO to v1.0:
- translation
- add more auth methods to gigachat API
- add new command 'balance' for [viewing token balance](https://developers.sber.ru/docs/ru/gigachat/api/reference/rest/post-tokens-count)

## QuickStart

1. Install the plugin in your Limnoria plugins directory.
2. Install dependencies *in your env* using pip:
```bash
pip3 install -r requirements.txt
```
3. Follow [official guide (in russian only)](https://developers.sber.ru/docs/ru/gigachat/individuals-quickstart#shag-1-sozdayte-proekt-giga-chat-api) to get auth credentials and set it in bot **privately**:
```
----- /query limnoria -----
    user │ @config supybot.plugins.GigaChat.auth_creds 27ebd34b1a854ae6a5...
limnoria │ user: The operation succeeded.
```
4. Use the `msg` command, if you're bot owner.
```
    user │ @msg Нужно ли мне следовать за белым кроликом?
limnoria │ user: Это зависит от того, куда он вас приведет.
```
5. If you want to allow other users to use the plugin, then use command below (for specified "user2").
```
   user2 │ @msg Как образовалась группа "Король и Шут"?
limnoria │ user2: Error: You don't have the gigachat capability...
    user │ @admin capability add user2 gigachat
limnoria │ user: The operation succeeded.
   user2 │ @msg Как образовалась группа "Король и Шут"?
limnoria │ user2: Группа «Король и Шут» была основана в Ленинграде в 1988 году
         │ Андреем Князевым и Александром Щиголевым. В то время они были
         │ студентами Ленинградского технологического института.
```
6. Also, you can allow using command for any user (without registered accounts too).
```
    user │ @defaultcapability remove -gigachat
limnoria │ user: The operation succeeded.
   user3 │ haha, i'm unregistered user!
   user3 │ @msg Напиши аннотацию из 20 слов к серии книг "Экспансия" Джеймса Кори
limnoria │ user3: Серия романов «Экспансия» — это захватывающий научно-
         │ фантастический цикл, который погружает читателя в мир будущего, где
         │ человечество колонизировало космос и столкнулось с новыми угрозами.
```

## Commands

*Note: user must have capability "gigachat" to use plugin (plugin provides default anti-capability "-gigachat" to prevent possible abuse). Just enter `admin capability add gigachat user` to give it him (see [Limnoria documentation about capabilities](https://docs.limnoria.net/use/capabilities.html#default)).*

- `msg <text>` sends given text to the AI and prints its answer:

```
    user │ @msg Кто ты, чудо?
limnoria │ user: Я — ваш личный помощник на сервере.
    user │ @msg who are you? (Speak english)
limnoria │ user: I am a chatbot, designed to help and provide information to
         │ users on the Internet Relay Chat network.
```

## Configuration

- **supybot.plugins.GigaChat.auth_creds** - string with authorization data to use GigaChat API. Plugin can't work without it.
    - Follow the [official guide](https://developers.sber.ru/docs/ru/gigachat/individuals-quickstart#shag-1-sozdayte-proekt-giga-chat-api) to get it.

- **supybot.plugins.GigaChat.verify_ssl_certs** - boolean that determines using ssl certs to verify connection.
    - `False` by default, because it uses russian original certs, but i highly recommend to install them in your python/system. Follow the [official guide](https://developers.sber.ru/docs/ru/gigachat/certificates).

- **supybot.plugins.GigaChat.new_line_symbol** - string that determines new line view.
    - Bot replaces all new line symbols (\n) in AI answers with this string. `" ↵ "` by default.

### Channel-specific

- **supybot.plugins.GigaChat.model** determines AI model.
    - `"GigaChat"` by default.
- **supybot.plugins.GigaChat.prompt** determines AI prompt.
    - `"Ты $botnick - IRC-бот. Будь вежлив и помогай пользователю."` by default.
- **supybot.plugins.GigaChat.max_tokens** determines max tokens that will be used for AI answer.
    - `256` by default.
