from gevent import Greenlet
from gevent import socket
import gevent
from NetBase.TransportRecvGreenlet import TransportRecvGreenlet
from NetBase.TransportSendGreenlet import TransportSendGreenlet

'''
客户端
'''
class TcpClient(Greenlet):
    def __init__(self, ip, port):
        Greenlet.__init__(self)
        self.addr = (ip, port)
        self.sendT = None
        self.recvT = None

    def setProtocol(self, protocol):
        self.protocol = protocol

    def close(self):
        if self.sendT is not None:
            self.sendT.close()

        if self.recvT is not None:
            self.recvT.kill()

    def _run(self):
        while True:
            try:
                self.skt = socket.socket()
                self.skt.connect(self.addr)
            except Exception as e:
                gevent.sleep(20) # 等待20秒，重复连接
                continue # 继续执行

            # 发送协程
            self.skt.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.sendT = TransportSendGreenlet(self.skt, self.addr)
            # 接收协程需要接收发送协程作为参数，用户回调时，将发送协程暴漏出去
            self.recvT = TransportRecvGreenlet(self.sendT, self.protocol)

            self.sendT.start()
            self.recvT.start()
            self.recvT.join()
            self.sendT = None
            self.recvT = None