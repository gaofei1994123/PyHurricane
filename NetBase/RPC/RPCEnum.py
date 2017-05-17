class RPCEnum(object):
    ASK_SIGNAL = "ASK"  # 客户端向服务器请求，并且有返回值
    NOTICE_SIGNAL = "NOTICE"  # 客户端向服务器请求，无返回值
    ANSWER_SIGNAL = "ANSWER"  # 服务器向客户端返回结果
    KEEP_LIVE = 'KEEPLIVE'  # 心跳保持 客户端发起
    REKEEP_LIVE = 'REKEEPLIVE'  # 心跳保持回复 服务端回复
    REGISTER = 'REGISTER' # 客户端连接后进行注册
    DEFAULT_TIMEOUT = 60  # 超时时间
    RPC_DATA_MAX_LENGTH = 10 * 1024 * 1024  # 10兆数据包，最大的rpc包