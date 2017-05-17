from NetBase.TcpClient import TcpClient
from NetBase.RPC.RPCClientProtocol import RPCClientProtocol,RemoteObject

class RPCClient(object):
    '''
    远程rpc ip port 初始化
    '''
    def __init__(self, ip, port, name, timeout=60):
        self.__tcpClient = TcpClient(ip=ip, port=port)
        self.__protocol = RPCClientProtocol(name)
        self.__tcpClient.setProtocol(self.__protocol)
        self.__remoteObject = RemoteObject(self.__protocol,timeout=timeout) # 10秒超时
        self.runing = False

    def connectRPCServer(self):
        if self.runing is False:
            self.__tcpClient.start()
            self.runing = True

    def Close(self):
        self.__tcpClient.close()

    def isConnect(self):
        return self.__protocol.connecting

    '''
    注册回调
    '''
    def registerMethod(self, method):
        self.__protocol.registerMethod(method)

    '''
    取消回调
    '''
    def deleteMethod(self, method):
        self.__protocol.deleteMethod(method)

    def registerServerCloseMethod(self, handler):
        self.__protocol.registerServerCloseMethod(handler)

    def registerServerConnectMethod(self, handler):
        self.__protocol.registerServerConnectMethod(handler)

    '''
    调用远程方法，需要返回值
    '''
    def callRemoteForResult(self, name, *args, **kw):
        if self.__protocol.connecting is False:
            raise Exception('远程rpc未建立连接')

        return self.__remoteObject.callRemoteForResult(name, *args, **kw)

    '''
    调用远程方法， 不需要返回值
    '''
    def callRemoteNotForResult(self, name, *args, **kw):
        if self.__protocol.connecting is False:
            raise Exception('远程rpc未建立连接')

        self.__remoteObject.callRemoteNotForResult(name, *args, **kw)
