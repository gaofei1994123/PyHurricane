from gevent import Greenlet
from gevent import socket
from NetBase.TransportRecvGreenlet import TransportRecvGreenlet
from NetBase.TransportSendGreenlet import TransportSendGreenlet

class TcpServer(Greenlet):
    def __init__(self, ip, port, listenNum = 1000):
        Greenlet.__init__(self)
        self.__ip = ip
        self.__port = port
        self.__listenNum = listenNum
        self.sessionno = 0

    def setProtocol(self, protocol):
        self.protocol = protocol

    def _run(self):
        self.skt = socket.socket()
        self.skt.bind((self.__ip, self.__port))
        self.skt.listen(self.__listenNum)
        while True:
            conn, addr = self.skt.accept()
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            sendT = TransportSendGreenlet(conn, addr, self.sessionno)
            recvT = TransportRecvGreenlet(sendT, self.protocol)

            sendT.start()  # 发送协程开启
            recvT.start()  # 接收协程开启
            self.sessionno += 1