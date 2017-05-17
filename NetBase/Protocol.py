# 用户需继承该类
class Protocol(object):
    # 连接回调
    def connectionMade(self, transport):
        pass

    # 关闭回调
    def connectionLost(self, transport, reason):
        pass

    #数据接收回调,将未处理完的数据包通过return返回
    def dataReceived(self, transport, data):
        return data
