# Gigachat AI plugin for Limnoria

[Limnoria](https://limnoria.net/) is IRC bot and this repo is an implementation of [Gigachat](https://developers.sber.ru/gigachat) API. Requires [gigachat](https://github.com/ai-forever/gigachat) module. Inspired by [ChatGPT limnoria plugin by oddluck](https://github.com/oddluck/limnoria-plugins/tree/master/ChatGPT).

TODO:
- translation
- maybe complex chatting with saving messages
- and managing them?..

## Commands

- `msg <text>` sends given text to the AI and prints its answer:

```
    user │ @msg Кто ты, чудо?
limnoria │ user: Я — ваш личный помощник на сервере.
    user │ @msg who are you? (Speak english)
limnoria │ user: I am a chatbot, designed to help and provide information to users on the Internet Relay Chat network.
```

*Note: plugin must be enabled in this channel. See **supybot.plugins.GigaChat.enabled** value.*

## Configuration

- **supybot.plugins.GigaChat.auth_creds** - string with authorization data to use GigaChat API.
    - Follow the [official guide](https://developers.sber.ru/docs/ru/gigachat/individuals-quickstart#shag-1-sozdayte-proekt-giga-chat-api) to get it.

- **supybot.plugins.GigaChat.verify_ssl_certs** - boolean that determines using ssl certs to verify connection.
    - `False` by default, because it uses russian original certs, but i highly recommend to install them in your python/system. Follow the [official guide](https://developers.sber.ru/docs/ru/gigachat/certificates).

- **supybot.plugins.GigaChat.new_line_symbol** - string that determines new line view.
    - Bot replaces all new line symbols (\n) in AI answers with this string. `" ↵ "` by default.

### Channel-specific

- **supybot.plugins.GigaChat.enabled** determines if AI enabled.
    - `False` by default.
- **supybot.plugins.GigaChat.model** determines AI model.
    - `"GigaChat"` by default.
- **supybot.plugins.GigaChat.prompt** determines AI prompt.
    - `"Ты $botnick - IRC-бот. Будь вежлив и помогай пользователю."` by default.
- **supybot.plugins.GigaChat.max_tokens** determines max tokens that will be used for AI answer.
    - `256` by default.

