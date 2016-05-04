from ..conf.auto_reply_definitions import autoreplies
from twisted.python import log

class AutoReply(object):
    def __init__(self):
        pass

    def process_message(self, message):
        prompt = str(message)
        for autoprompt, autorepsonse in autoreplies.iteritems():
            if autoprompt in prompt:
                log.msg("Responding with '{}' to {} (trigger was '{}')".format(autorepsonse, message.nickname, prompt))
                message.channel.msg(autorepsonse)
                break
