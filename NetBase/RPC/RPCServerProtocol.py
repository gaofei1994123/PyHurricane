
from NetBase.RPC.RPCBaseProtocol import RPCBaseProtocol
from NetBase.RPC.RPCEnum import RPCEnum
from NetBase.RPC.RPCError import RPCDataTooLongError
import struct
import gevent
import marshal
from NetBase.RPC.AsyncResultFactory import AsyncResultFactory

'''
远程调用对象，rpc客户端使用
'''
class RemoteObjectServer(object):
    def __init__(self, broker, timeout = RPCEnum.DEFAULT_TIMEOUT):
        self.__broker = broker
        self.__timeout = timeout

    '''
    _name 远程方法名称
    args kw 远程方法参数
    '''
    def callRemoteForResult(self, clientname, name, *args, **kw):
        key, result = AsyncResultFactory().createAsyncResult()
        self.__broker.sendMessage(clientname, key, name, *args, **kw)
        try:
            return result.get(timeout=self.__timeout)
        except (Exception, gevent.Timeout) as e:
            AsyncResultFactory().dropAsyncResultBykey(key)
            return '调用超时,超时时长:%s' % e

    def callRemoteNotForResult(self, clientname, name, *args, **kw):
        self.__broker.sendMessage(clientname, None, name, *args, **kw)

class RPCServerProtocol(RPCBaseProtocol):
    def __init__(self):
        RPCBaseProtocol.__init__(self)
        self.__clientDict = {}
        self.__clientName = []
        self.__clientCloseHandler = None
        self.__clientConnectHandler = None

    def registerClientCloseMethod(self, handler):
        self.__clientCloseHandler = handler

    def registerClientConnectMethod(self, handler):
        self.__clientConnectHandler = handler

    def connectionLost(self, transport, reason):
        try:
            if transport.name is None:
                pass
            else:
                if transport.name in self.__clientDict:
                    del self.__clientDict[transport.name]
                if transport.name in self.__clientName:
                    self.__clientName.remove(transport.name)

                if self.__clientCloseHandler is not None:
                    self.__clientCloseHandler(transport.name)
        except Exception as e:
            pass

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
        if msgType == RPCEnum.ASK_SIGNAL or msgType == RPCEnum.NOTICE_SIGNAL: # 客户端调用
            self.askReceived(transport, request)
        elif msgType == RPCEnum.KEEP_LIVE: # 客户端心跳
            data = marshal.dumps({'msgtype': RPCEnum.REKEEP_LIVE})
            len = data.__len__()
            transport.sendall(struct.pack("!i", len) + data)
        elif msgType == RPCEnum.REGISTER: # 客户端注册
            transport.name = request['name']
            self.__clientDict[transport.name] = transport
            if transport.name not in self.__clientName:
                self.__clientName.append(transport.name)
            if self.__clientConnectHandler is not None:
                self.__clientConnectHandler(transport.name)
        elif msgType == RPCEnum.ANSWER_SIGNAL:
            self.answerReceived(request)

    '''
    向对应名称的客户端发送远程调用命令
    '''
    def sendMessage(self, clientname, key, name, *args, **kw):
        if clientname not in self.__clientDict:
            raise Exception('客户端 %s 不在线' % clientname)

        transport = self.__clientDict[clientname]
        if key is None:
            messageType = RPCEnum.ASK_SIGNAL
        else:
            messageType = RPCEnum.NOTICE_SIGNAL

        data = marshal.dumps({'msgtype': messageType, 'key': key, 'name': name, 'args': args, 'kw': kw})
        len = data.__len__()
        if len > RPCEnum.RPC_DATA_MAX_LENGTH:
            raise RPCDataTooLongError

        transport.sendall(struct.pack("!i", len) + data)