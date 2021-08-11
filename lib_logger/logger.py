from enum import Enum, unique, auto
from typing import Literal
import discord as dc
import datetime as dt

from discord.message import Attachment


@unique
class EnumLog(Enum):
    ME_READY               = auto()     # BOT 準備完了
    TYPING                 = auto()     # メッセージ入力中
    MESSAGE_SEND           = auto()     # メッセージ送信
    MESSAGE_DELETE         = auto()     # メッセージ削除
    MESSAGE_EDIT           = auto()     # メッセージ編集
    MESSAGE_PINS_UPDATE    = auto()     # メッセージがピン留め/解除
    REACTION_ADD           = auto()     # リアクション追加
    REACTION_DELETE        = auto()     # リアクション削除
    CHANNEL_CREATE         = auto()     # チャンネル作成
    CHANNEL_DELETE         = auto()     # チャンネル削除
    CHANNEL_UPDATE         = auto()     # チャンネル更新
    THREAD_JOIN            = auto()     # スレッド追加(作成/アーカイブから復帰)
    THREAD_DELETE          = auto()     # スレッド削除
    THREAD_UPDATE          = auto()     # スレッド更新
    THREAD_MEMBER_JOIN     = auto()     # スレッドにメンバ参加
    THREAD_MEMBER_LEAVE    = auto()     # スレッドからメンバ退出
    MEMBER_PROFILE_UPDATE  = auto()     # サーバ参加で与えられるメンバ情報が更新 : ニックネーム / 役職 / pending(なにこれ) etc
    MEMBER_PRESENCE_UPDATE = auto()     # メンバステータス更新 : オンラインステータス / アクティビティ(プレイ中ゲーム)
    USER_PROFILE_UPDATE    = auto()     # ユーザの情報が更新 : ユーザ名 / アイコン / ID などのユーザ固有の情報 etc
    GUILD_UPDATE           = auto()     # ギルド情報の更新 : ギルド名 / AFKチャンネルの変更・タイムアウト時間の変更 etc
    GUILD_ROLE_CREATE      = auto()     # 役職作成
    GUILD_ROLE_DELETE      = auto()     # 役職削除
    GUILD_ROLE_UPDATE      = auto()     # 役職更新
    GUILD_EMOJI_UPDATE     = auto()     # 絵文字作成/削除
    GUILD_STICKER_UPDATE   = auto()     # ステッカー作成/削除
    VOICE_UPDATE           = auto()     # ボイスチャンネルの状態更新 : メンバ参加/退出
    MEMBER_BAN             = auto()     # メンバBAN
    MEMBER_UNBAN           = auto()     # メンバBAN解除
    INVITE_CREATE          = auto()     # 招待作成
    INVITE_DELETE          = auto()     # 招待解除



class DiscordLogging:
    def __init__(self, bot_name: str):
        
        self.__bot_name = bot_name
        
        self.__func_dict = {
            EnumLog.ME_READY                : self.__func_ME_READY                  ,
            EnumLog.TYPING                  : self.__func_TYPING                    ,
            EnumLog.MESSAGE_SEND            : self.__func_MESSAGE_SEND              ,
            EnumLog.MESSAGE_DELETE          : self.__func_MESSAGE_DELETE            ,
            EnumLog.MESSAGE_EDIT            : self.__func_MESSAGE_EDIT              ,
            EnumLog.MESSAGE_PINS_UPDATE     : self.__func_MESSAGE_PINS_UPDATE       ,
            EnumLog.REACTION_ADD            : self.__func_REACTION_ADD              ,
            EnumLog.REACTION_DELETE         : self.__func_REACTION_DELETE           ,
            EnumLog.CHANNEL_CREATE          : self.__func_CHANNEL_CREATE            ,
            EnumLog.CHANNEL_DELETE          : self.__func_CHANNEL_DELETE            ,
            EnumLog.CHANNEL_UPDATE          : self.__func_CHANNEL_UPDATE            ,
            EnumLog.THREAD_JOIN             : self.__func_THREAD_JOIN               ,
            EnumLog.THREAD_DELETE           : self.__func_THREAD_DELETE             ,
            EnumLog.THREAD_UPDATE           : self.__func_THREAD_UPDATE             ,
            EnumLog.THREAD_MEMBER_JOIN      : self.__func_THREAD_MEMBER_JOIN        ,
            EnumLog.THREAD_MEMBER_LEAVE     : self.__func_THREAD_MEMBER_LEAVE       ,
            EnumLog.MEMBER_PROFILE_UPDATE   : self.__func_MEMBER_PROFILE_UPDATE     ,
            EnumLog.MEMBER_PRESENCE_UPDATE  : self.__func_MEMBER_PRESENCE_UPDATE    ,
            EnumLog.USER_PROFILE_UPDATE     : self.__func_USER_PROFILE_UPDATE       ,
            EnumLog.GUILD_UPDATE            : self.__func_GUILD_UPDATE              ,
            EnumLog.GUILD_ROLE_CREATE       : self.__func_GUILD_ROLE_CREATE         ,
            EnumLog.GUILD_ROLE_DELETE       : self.__func_GUILD_ROLE_DELETE         ,
            EnumLog.GUILD_ROLE_UPDATE       : self.__func_GUILD_ROLE_UPDATE         ,
            EnumLog.GUILD_EMOJI_UPDATE      : self.__func_GUILD_EMOJI_UPDATE        ,
            EnumLog.GUILD_STICKER_UPDATE    : self.__func_GUILD_STICKER_UPDATE      ,
            EnumLog.VOICE_UPDATE            : self.__func_VOICE_UPDATE              ,
            EnumLog.MEMBER_BAN              : self.__func_MEMBER_BAN                ,
            EnumLog.MEMBER_UNBAN            : self.__func_MEMBER_UNBAN              ,
            EnumLog.INVITE_CREATE           : self.__func_INVITE_CREATE             ,
            EnumLog.INVITE_DELETE           : self.__func_INVITE_DELETE
        }


    async def log(self, type: Literal, channel: dc.TextChannel, data: any):
        # launch
        await self.__func_dict[type](channel, data)
    

    def __convert(self, type: Literal, content: str) -> str:
        return ":speech_balloon:  `{0}:{1}:{2}:`\n{3}".format(self.__bot_name, type.name, dt.datetime.now().strftime("%Y-%m-%d--%H-%M-%S"), content)
    

    # data -> None    
    async def __func_ME_READY(self, channel: dc.TextChannel, data):
        await channel.send(self.__convert(EnumLog.ME_READY, "BOT ready"))


    # data -> [discord.Channel, Union[discord.Member, discord.Member], datetime.datetime]
    async def __func_TYPING(self, channel: dc.TextChannel, data: list):
        # data
        typing_ch: dc.abc.Messageable = data[0]
        member   : dc.Member          = data[1]
        # date     : dt.datetime        = data[2]
        
        await channel.send(self.__convert(EnumLog.TYPING, "{0}({1}) is typing on {2}({3}).".format(
                    member.nick if member.nick is not None else member.name,
                    member.id,
                    typing_ch.name,
                    typing_ch.id)))


    # data -> discord.Message
    async def __func_MESSAGE_SEND(self, channel: dc.TextChannel, data: dc.Message):
        # currently, only one file can be attached to a message

        # get files (>=2)
        # files = []
        # if data.attachments:
        #     for attach in data.attachments:
        #         files.append(await attach.to_file())

        # get file (only 1)
        file = await data.attachments[0].to_file() if data.attachments else None

        # send log message
        await channel.send(self.__convert(EnumLog.MESSAGE_SEND, "{0}({1}) send a meesage {2}:\n{3}".format(
                    data.author.nick if data.author.nick is not None else data.author.name,
                    data.author.id,
                    # "with {0} {1} ".format(len(files), "file" if len(files) == 1 else "files") if data.attachments else "",
                    "with file " if file is not None else "",
                    data.content)),
                file=file)
        # send file
        # for f in files:
        #     await channel.send("", file=f)



    async def __func_MESSAGE_DELETE(self, channel: dc.TextChannel, data):
        pass

    async def __func_MESSAGE_EDIT(self, channel: dc.TextChannel, data):
        pass

    async def __func_MESSAGE_PINS_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_REACTION_ADD(self, channel: dc.TextChannel, data):
        pass

    async def __func_REACTION_DELETE(self, channel: dc.TextChannel, data):
        pass

    async def __func_CHANNEL_CREATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_CHANNEL_DELETE(self, channel: dc.TextChannel, data):
        pass

    async def __func_CHANNEL_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_THREAD_JOIN(self, channel: dc.TextChannel, data):
        pass

    async def __func_THREAD_DELETE(self, channel: dc.TextChannel, data):
        pass

    async def __func_THREAD_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_THREAD_MEMBER_JOIN(self, channel: dc.TextChannel, data):
        pass

    async def __func_THREAD_MEMBER_LEAVE(self, channel: dc.TextChannel, data):
        pass

    async def __func_MEMBER_PROFILE_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_MEMBER_PRESENCE_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_USER_PROFILE_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_GUILD_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_GUILD_ROLE_CREATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_GUILD_ROLE_DELETE(self, channel: dc.TextChannel, data):
        pass

    async def __func_GUILD_ROLE_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_GUILD_EMOJI_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_GUILD_STICKER_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_VOICE_UPDATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_MEMBER_BAN(self, channel: dc.TextChannel, data):
        pass

    async def __func_MEMBER_UNBAN(self, channel: dc.TextChannel, data):
        pass

    async def __func_INVITE_CREATE(self, channel: dc.TextChannel, data):
        pass

    async def __func_INVITE_DELETE(self, channel: dc.TextChannel, data):
        pass
