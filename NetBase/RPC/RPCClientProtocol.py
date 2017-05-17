from NetBase.RPC.RPCBaseProtocol import RPCBaseProtocol
from NetBase.RPC.RPCEnum import RPCEnum
from NetBase.RPC.RPCError import RPCDataTooLongError
from NetBase.RPC.AsyncResultFactory import AsyncResultFactory
from gevent import Greenlet
import struct
import gevent
import marshal

'''
远程调用对象，rpc客户端使用
'''
class RemoteObject(object):
    def __init__(self, broker, timeout = RPCEnum.DEFAULT_TIMEOUT):
        self.__broker = broker
        self.__timeout = timeout

    '''
    name 远程方法名称
    args kw 远程方法参数
    '''
    def callRemoteForResult(self, name, *args, **kw):
        key, result = AsyncResultFactory().createAsyncResult()
        self.__broker.sendMessage(key, name, *args, **kw)

        try:
            return result.get(timeout=self.__timeout)
        except (Exception, gevent.Timeout) as e:
            AsyncResultFactory().dropAsyncResultBykey(key)
            raise Exception('调用超时,超时时长:%s' % e)

    def callRemoteNotForResult(self, name, *args, **kw):
        self.__broker.sendMessage(None, name, *args, **kw)

class RPCClientProtocol(RPCBaseProtocol):
    def __init__(self, name):
        RPCBaseProtocol.__init__(self)
        self.__transport = None
        self.connecting = False
        self.__name = name
        self.__serverCloseHandler = None
        self.__serverConnectHandler = None
        gevent.spawn(self.__sendKeepLive)

    def registerServerCloseMethod(self, handler):
        self.__serverCloseHandler = handler

    def registerServerConnectMethod(self, handler):
        self.__serverConnectHandler = handler

    def connectionMade(self, transport):
        self.transport = transport
        self.connecting = True
        data = marshal.dumps({'msgtype': RPCEnum.REGISTER, 'name': self.__name})
        self.transport.sendall(struct.pack("!i", data.__len__()) + data)
        if self.__serverConnectHandler is not None:
            self.__serverConnectHandler()

        # 关闭回调
    def connectionLost(self, transport, reason):
        self.connecting = False
        self.transport = None
        if self.__serverCloseHandler is not None:
            self.__serverCloseHandler()

    '''
    心跳协程
    '''
    def __sendKeepLive(self):
        while True:
            gevent.sleep(30)
            if self.connecting is True:
                try:
                    data = marshal.dumps({'msgtype': RPCEnum.KEEP_LIVE})
                    len = data.__len__()
                    self.transport.sendall(struct.pack("!i", len) + data)
                except Exception as e:
                    continue

    '''
    发送远程调用命令
    '''
    def sendMessage(self, key, name, *args, **kw):
        if self.connecting is False:
            raise Exception('未连接远程rpc服务')

        if key is None:
            messageType = RPCEnum.ASK_SIGNAL
        else:
            messageType = RPCEnum.NOTICE_SIGNAL

        data = marshal.dumps({'msgtype':messageType, 'key':key, 'name':name, 'args':args, 'kw':kw})
        len = data.__len__()
        if len > RPCEnum.RPC_DATA_MAX_LENGTH:
            raise RPCDataTooLongError

        self.transport.sendall(struct.pack("!i", len) + data)

    def dataReceived(self, transport, data):
        while True:
            if data.__len__() < 4:
                return data

            len, = struct.unpack("!i", data[:4])
            len += 4
            if len > data.__len__():
                return data

            frameData = data[4:len] # 一帧有效数据
            gevent.spawn(self.__msgReslove, transport, frameData)
            data = data[len:] # 剩余的

    def __msgReslove(self, transport, data):
        request = marshal.loads(data)
        msgType = request['msgtype']
        if msgType == RPCEnum.ANSWER_SIGNAL:
            self.answerReceived(request)
        elif msgType == RPCEnum.ASK_SIGNAL or msgType == RPCEnum.NOTICE_SIGNAL: # 服务器端调用
            self.askReceived(transport, request)
        elif msgType == RPCEnum.REKEEP_LIVE: # 心跳回复
            pass