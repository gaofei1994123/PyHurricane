from NetBase.Protocol import Protocol
from NetBase.RPC.RPCEnum import RPCEnum
from NetBase.RPC.RPCError import RPCDataTooLongError
import struct
import marshal
from NetBase.RPC.AsyncResultFactory import AsyncResultFactory

class RPCBaseProtocol(Protocol):
    def __init__(self):
        Protocol.__init__(self)
        self.__methodDict = {}

    '''
    注册回调
    '''
    def registerMethod(self, method):
        self.__methodDict[method.__name__] = method

    '''
    取消回调
    '''
    def deleteMethod(self, method):
        if method.__name__ in self.__methodDict:
            del self.__methodDict[method.__name__]

    '''
    rpc请求
    '''
    def askReceived(self, transport, request):
        key = request['key']
        name = request['name']
        args = request['args']
        kw = request['kw']

        result = None
        error = None
        try:
            if name in self.__methodDict:
                method = self.__methodDict[name]
                result = method(*args, **kw)
            else:
                error = '找不到对应的回调函数，函数名:%s' % name
        except Exception as e:
            result = None
            error = str(e)

        if key != None:
            response = {'msgtype':RPCEnum.ANSWER_SIGNAL, 'key':key, 'result':result, 'error':error}
            _response = marshal.dumps(response)
            if _response.__len__() + 4 > RPCEnum.RPC_DATA_MAX_LENGTH:
                raise RPCDataTooLongError
            transport.sendall(struct.pack('!i', _response.__len__()) + _response)

    '''
    rpc应答
    '''
    def answerReceived(self, request):
        key = request['key']
        result = request['result']
        error = request['error']
        aresult = AsyncResultFactory().popAsyncResult(key)
        if error is None:
            aresult.set(result)
        else:
            aresult.set(result)
            raise Exception(error)