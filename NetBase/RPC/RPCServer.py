from NetBase.RPC.RPCServerProtocol import RemoteObjectServer
from NetBase.TcpServer import TcpServer
from NetBase.RPC.RPCServerProtocol import RPCServerProtocol
from NetBase.RPC.RPCEnum import RPCEnum


class RPCServer(object):
    '''
    远程rpc ip port 初始化
    '''
    def __init__(self, ip, port, timeout = RPCEnum.DEFAULT_TIMEOUT):
        self.__tcpServer = TcpServer(ip=ip, port=port)
        self.__protocol = RPCServerProtocol()
        self.__tcpServer.setProtocol(self.__protocol)
        self.__remoteObject = RemoteObjectServer(self.__protocol, timeout)
        self.__runing = False

    '''
    开始接收请求
    '''
    def listenRPCClient(self):
        if self.__runing is False:
            self.__tcpServer.start()
            self.__runing = True

    '''
    调用远程方法，需要返回值
    '''
    def callRemoteForResult(self, clientname, name, *args, **kw):
        return self.__remoteObject.callRemoteForResult(clientname, name, *args, **kw)

    '''
    调用远程方法， 不需要返回值
    '''
    def callRemoteNotForResult(self, clientname, name, *args, **kw):
        self.__remoteObject.callRemoteNotForResult(clientname, name, *args, **kw)

    '''
    注册远程调用函数
    '''
    def registerMethod(self, method):
        self.__protocol.registerMethod(method)

    def registerClientCloseMethod(self, handler):
        self.__protocol.registerClientCloseMethod(handler)

    def registerClientConnectMethod(self, handler):
        self.__protocol.registerClientConnectMethod(handler)

    '''
    取消远程调用函数
    '''
    def deleteMethod(self, method):
        self.__protocol.deleteMethod(method)
