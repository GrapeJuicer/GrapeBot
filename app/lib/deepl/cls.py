from deepl import Language, Translator, SplitSentences, Formality, GlossaryInfo, TextResult
from discord import app_commands, Interaction
from typing import Optional, Union, Dict, Iterable, List
from sqlite3 import Connection
from datetime import datetime


class DcLanguageList:
    # total 28
    SOURCE = [
        app_commands.Choice(name='自動検知', value=""),
        app_commands.Choice(name='ブルガリア語', value=Language.BULGARIAN),
        app_commands.Choice(name='チェコ語', value=Language.CZECH),
        app_commands.Choice(name='デンマーク語', value=Language.DANISH),
        app_commands.Choice(name='ドイツ語', value=Language.GERMAN),
        app_commands.Choice(name='ギリシャ語', value=Language.GREEK),
        app_commands.Choice(name='英語', value=Language.ENGLISH),
        app_commands.Choice(name='スペイン語', value=Language.SPANISH),
        # app_commands.Choice(name='エストニア語', value=Language.ESTONIAN),
        app_commands.Choice(name='フィンランド語', value=Language.FINNISH),
        app_commands.Choice(name='フランス語', value=Language.FRENCH),
        app_commands.Choice(name='ハンガリー語', value=Language.HUNGARIAN),
        app_commands.Choice(name='インドネシア語', value=Language.INDONESIAN),
        app_commands.Choice(name='イタリア語', value=Language.ITALIAN),
        app_commands.Choice(name='日本語', value=Language.JAPANESE),
        # app_commands.Choice(name='リトアニア語', value=Language.LITHUANIAN),
        app_commands.Choice(name='ラトビア語', value=Language.LATVIAN),
        app_commands.Choice(name='オランダ語', value=Language.DUTCH),
        app_commands.Choice(name='ポーランド語', value=Language.POLISH),
        app_commands.Choice(name='ポルトガル語', value=Language.PORTUGUESE),
        app_commands.Choice(name='ルーマニア語', value=Language.ROMANIAN),
        app_commands.Choice(name='ロシア語', value=Language.RUSSIAN),
        # app_commands.Choice(name='スロバキア語', value=Language.SLOVAK),
        # app_commands.Choice(name='スロベニア語', value=Language.SLOVENIAN),
        app_commands.Choice(name='スウェーデン語', value=Language.SWEDISH),
        app_commands.Choice(name='トルコ語', value=Language.TURKISH),
        app_commands.Choice(name='ウクライナ語', value=Language.UKRAINIAN),
        app_commands.Choice(name='中国語', value=Language.CHINESE),
    ]
    # 29
    TARGET = [
        app_commands.Choice(name='ブルガリア語', value=Language.BULGARIAN),
        app_commands.Choice(name='チェコ語', value=Language.CZECH),
        app_commands.Choice(name='デンマーク語', value=Language.DANISH),
        app_commands.Choice(name='ドイツ語', value=Language.GERMAN),
        app_commands.Choice(name='ギリシャ語', value=Language.GREEK),
        app_commands.Choice(name='英語（アメリカ）', value=Language.ENGLISH_AMERICAN),
        app_commands.Choice(name='英語（イギリス）', value=Language.ENGLISH_BRITISH),
        app_commands.Choice(name='スペイン語', value=Language.SPANISH),
        # app_commands.Choice(name='エストニア語', value=Language.ESTONIAN),
        app_commands.Choice(name='フィンランド語', value=Language.FINNISH),
        app_commands.Choice(name='フランス語', value=Language.FRENCH),
        app_commands.Choice(name='ハンガリー語', value=Language.HUNGARIAN),
        app_commands.Choice(name='インドネシア語', value=Language.INDONESIAN),
        app_commands.Choice(name='イタリア語', value=Language.ITALIAN),
        app_commands.Choice(name='日本語', value=Language.JAPANESE),
        # app_commands.Choice(name='リトアニア語', value=Language.LITHUANIAN),
        app_commands.Choice(name='ラトビア語', value=Language.LATVIAN),
        app_commands.Choice(name='オランダ語', value=Language.DUTCH),
        app_commands.Choice(name='ポーランド語', value=Language.POLISH),
        app_commands.Choice(name='ポルトガル語', value=Language.PORTUGUESE_EUROPEAN),
        app_commands.Choice(name='ポルトガル語（ブラジル）', value=Language.PORTUGUESE_BRAZILIAN),
        app_commands.Choice(name='ルーマニア語', value=Language.ROMANIAN),
        app_commands.Choice(name='ロシア語', value=Language.RUSSIAN),
        # app_commands.Choice(name='スロバキア語', value=Language.SLOVAK),
        # app_commands.Choice(name='スロベニア語', value=Language.SLOVENIAN),
        app_commands.Choice(name='スウェーデン語', value=Language.SWEDISH),
        app_commands.Choice(name='トルコ語', value=Language.TURKISH),
        app_commands.Choice(name='ウクライナ語', value=Language.UKRAINIAN),
        app_commands.Choice(name='中国語', value=Language.CHINESE),
    ]



class LoggingTranslator(Translator):
    def __init__(
        self,
        auth_key            : str,
        connection          : Connection,
        *,
        server_url          : Optional[str]          = None,
        proxy               : Union[Dict, str, None] = None,
        skip_language_check : bool                   = False
    ):
        super().__init__(
            auth_key,
            server_url          = server_url,
            proxy               = proxy,
            skip_language_check = skip_language_check
        )

        self.connection = connection

        cur = self.connection.cursor()
        cur.execute(
            'create table if not exists gb_deepl( \
                id integer primary key autoincrement, \
                date datetime not null,           \
                guild_id int not null,            \
                user_id text not null,            \
                source_text text not null,        \
                target_text text not null,        \
                source_language text,             \
                target_language text not null     \
            )'
        )
        self.connection.commit()
        cur.close()

    def translate_text(
        self                                                                      ,
        ctx                 : Interaction                                         ,
        text                : Union[str, Iterable[str]]                           ,
        *                                                                         ,
        source_lang         : Union[str, Language, None]     = None               ,
        target_lang         : Union[str, Language]                                ,
        split_sentences     : Union[str, SplitSentences]     = SplitSentences.ALL ,
        preserve_formatting : bool                           = False              ,
        formality           : Union[str, Formality]          = Formality.DEFAULT  ,
        glossary            : Union[str, GlossaryInfo, None] = None               ,
        tag_handling        : Optional[str]                  = None               ,
        outline_detection   : bool                           = True               ,
        non_splitting_tags  : Union[str, List[str], None]    = None               ,
        splitting_tags      : Union[str, List[str], None]    = None               ,
        ignore_tags         : Union[str, List[str], None]    = None
    ) -> Union[TextResult, List[TextResult]]:
        tt = super().translate_text(
            text                                      ,
            source_lang         = source_lang         ,
            target_lang         = target_lang         ,
            split_sentences     = split_sentences     ,
            preserve_formatting = preserve_formatting ,
            formality           = formality           ,
            glossary            = glossary            ,
            tag_handling        = tag_handling        ,
            outline_detection   = outline_detection   ,
            non_splitting_tags  = non_splitting_tags  ,
            splitting_tags      = splitting_tags      ,
            ignore_tags         = ignore_tags
        )
        cur = self.connection.cursor()
        cur.execute(
            "insert into gb_deepl \
            (date, guild_id, user_id, source_text, target_text, source_language, target_language) \
            values (?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now(),
                ctx.guild_id,
                ctx.user.id,
                text,
                tt.text,
                source_lang,
                target_lang,
            )
        )
        self.connection.commit()
        cur.close()
        return tt
