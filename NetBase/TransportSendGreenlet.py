from gevent import Greenlet, queue

'''
发送协程
'''
class TransportSendGreenlet(Greenlet):
    def __init__(self, skt, address, sessionno=0, maxSendlen = 10 * 1024 * 1024):
        Greenlet.__init__(self)
        self.skt = skt
        self.address = address
        self.sessionno = sessionno
        self.inbox = queue.Queue()
        self.maxSendlen = maxSendlen # 最大待发送数据，用户可以通过设置此参数，改变最大的发送缓冲buffer大小
        self.notSendlen = 0
        self.runing = True

    def getAddress(self):
        """
        获取对方地址
        """
        return self.address

    def close(self):
        self.runing = False
        self.skt.close()

    def recv(self, *args):
        return self.skt.recv(*args)

    def sendall(self, data):
        if self.notSendlen + data.__len__() >= self.maxSendlen:
            return False

        self.notSendlen += data.__len__()
        self.inbox.put(data)
        return True

    def _run(self):
        while self.runing:
            message = self.inbox.get()

            while message.__len__() < 4096: # 小于4k,组装成大包再发送
                if self.inbox.__len__() > 0:
                    message += self.inbox.get()
                else:
                    break

            try:
                self.skt.send(message)
            except Exception as e:
                self.runing = False # 将异常抛给接收协程去处理
                return

            self.notSendlen -= message.__len__()