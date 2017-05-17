from gevent import Greenlet

'''
接收协程
'''
class TransportRecvGreenlet(Greenlet):
    def __init__(self, transport, protocol):
        Greenlet.__init__(self)
        self.__transport = transport
        self.__protocol = protocol
        self.__recvBuffer = bytearray(0)

    def _run(self):
        # 连接回调
        self.__protocol.connectionMade(self.__transport)
        try:
            while True:
                data = self.__transport.recv(1024)
                if not data:
                    break

                self.__recvBuffer += data
                # 数据包到来回调
                self.__recvBuffer = self.__protocol.dataReceived(self.__transport, self.__recvBuffer)

        except Exception as e:
            # 断开连接回调
            self.__protocol.connectionLost(self.__transport, reason=e)
        else:
            self.__protocol.connectionLost(self.__transport, reason=None)
        finally:
            self.__transport.close()
            self.__transport.kill() # 销毁发送协程

