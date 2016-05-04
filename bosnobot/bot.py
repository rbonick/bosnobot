from twisted.python import log
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

from bosnobot.conf import settings
from bosnobot.pool import ChannelPool
from bosnobot.channel import Channel
from bosnobot.message import MessageDispatcher, Message


class IrcProtocol(irc.IRCClient):
    def lineReceived(self, line):
        # print line
        irc.IRCClient.lineReceived(self, line)
    
    def sendLine(self, line):
        # print "sending %s" % repr(line)
        irc.IRCClient.sendLine(self, line)
        
    def connectionMade(self):
        self.channel_pool = ChannelPool(self)
        self.nickname = self.botnick
        log.msg("Loaded bot {}".format(self.nickname))
        self.password = settings.BOT_PASSWORD
        irc.IRCClient.connectionMade(self)
        self._initialize_bot()
    
    def connectionLost(self, reason):
        log.msg("Connection lost")
        self.bot.shutdown()
    
    def _initialize_bot(self):
        self.bot = IrcBot(self)
    
    def signedOn(self):
        # once signed on to the irc server join each channel.
        for channel in self.bot.channels:
            self.channel_pool.join(channel)
        self.bot.initialize()
    
    def joined(self, channel):
        channel = self.channel_pool.get(channel)
        channel.joined = True
        log.msg("joined %s" % channel.name)
    
    def privmsg(self, user, channel, msg):
        self.dispatch_message(user, channel, msg)
    
    def action(self, user, channel, msg):
        # @@@ passing in as kwarg until event refactor is complete
        self.dispatch_message(user, channel, msg, action=True)
    
    def dispatch_message(self, user, channel, msg, **kwargs):
        if self.channel_pool.joined_all:
            channel = self.channel_pool.get(channel)
            message = Message(user, channel, msg, self.nickname, **kwargs)
            self.factory.message_dispatcher.dispatch(message)


class IrcBot(object):
    channels = []
    
    def __init__(self, protocol):
        self.protocol = protocol
        for channel in settings.BOT_CHANNELS:
            self.channels.append(Channel(channel))
    
    def initialize(self):
        pass
    
    def shutdown(self):
        pass


class IrcBotFactory(protocol.ClientFactory):
    protocol = IrcProtocol
    message_dispatcher_class = MessageDispatcher
    
    def __init__(self, botnick, channels):
        self.botnick = botnick
        self.channels = channels
    
    def clientConnectionFailed(self, connector, reason):
        log.msg("connection failed: %s" % reason)
        reactor.stop()
    
    def startFactory(self):
        self.message_dispatcher = self.message_dispatcher_class()
    
    def stopFactory(self):
        self.message_dispatcher.stop()

    def buildProtocol(self, addr):
        """
        Create an instance of a subclass of Protocol.

        The returned instance will handle input on an incoming server
        connection, and an attribute "factory" pointing to the creating
        factory.

        Alternatively, C{None} may be returned to immediately close the
        new connection.

        Override this method to alter how Protocol instances get created.

        @param addr: an object implementing L{twisted.internet.interfaces.IAddress}
        """
        p = self.protocol()
        p.factory = self
        p.botnick = self.botnick
        return p
