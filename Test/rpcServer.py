from NetBase.RPC.RPCServer import RPCServer

import gevent

def Add(*args, **kwargs):
    a = 0
    for i in args:
        a += i

    return a

def ClientConnectCallback(clientName):
    print('%s connect' % clientName)

def ClientCloseCallback(clientName):
    print('%s close' % clientName)

rpcServer = RPCServer('127.0.0.1', 10000)
rpcServer.registerMethod(Add)
rpcServer.registerClientConnectMethod(ClientConnectCallback)
rpcServer.registerClientCloseMethod(ClientCloseCallback)

rpcServer.listenRPCClient()

while True:
    gevent.sleep(1)