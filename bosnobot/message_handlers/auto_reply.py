from bosnobot.conf.auto_reply_definitions import autoreplies
from twisted.python import log


class AutoReply(object):
    def __init__(self):
        pass

    def process_message(self, message):
        botReplies = autoreplies[message.botNick]
        prompt = str(message)
        for autoprompt, autorepsonse in botReplies.iteritems():
            if autoprompt in prompt:
                log.msg("{}: Responding with '{}' to {} (trigger was '{}')".format(message.botNick, autorepsonse, message.nickname, prompt))
                message.channel.msg(autorepsonse, True)
                break
