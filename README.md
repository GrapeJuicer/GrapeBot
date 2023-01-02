# GrapeBot

- [GrapeBot](#grapebot)
  - [Summary](#summary)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Contact](#contact)


## Summary

**Grape Bot** is a discord bot.
It provides following services.

- [Vote (Open)](docs/vote_open.md)
- [Vote (Anonymous)](docs/vote_anonymous.md)
- [DeepL Translate](docs/deepl.md)

## Requirements

- docker (*Confirmed*: version `20.10.22`, build `3a2c30b`)

## Installation

1. Build docker image.

    ```
    $ docker build --tag grapebot:1.0
    ```

2. Create container and run it with keys.

    ```
    $ docker run -d --name grapebot-v1.0 -v /path/to/discord_token:/app/token.key -v /path/to/deepl_api_key:/app/deepl.key grapebot:1.0
    ```

    If you want to mount database, add param like:

    ```
   -v /path/to/db:/app/db.sqlite3
    ```

    **note** : If `sqlite3.OperationalError: attempt to write a readonly database` is occured, run following command.
    ```
    $ chmod 777 /path/to/db
    ```

## Contact

|  About  |                                               |
| :-----: | :-------------------------------------------- |
|  Name   | ぶどうじゅーす / GrapeJuice                   |
|  Mail   | Dev.Grape@outlook.jp                          |
| Twitter | [@G__HaC](https://www.twitter.com/G__HaC)     |
| GitHub  | [GrapeJuicer](https://github.com/GrapeJuicer) |
