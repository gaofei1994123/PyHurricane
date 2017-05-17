from NetBase.RPC.RPCClient import RPCClient

global connect
connect = False

def Connect():
    global connect
    print('rpc server connect')
    connect = True

rpcClient = RPCClient('127.0.0.1', 10000, 'client1', timeout=60)
rpcClient.registerServerConnectMethod(Connect)

rpcClient.connectRPCServer()

while True:
    if connect is False:
        import gevent
        gevent.sleep(1)
    else:
        break

addresult = rpcClient.callRemoteForResult('Add', 10, 20, 30)
print(addresult)

rpcClient.Close()