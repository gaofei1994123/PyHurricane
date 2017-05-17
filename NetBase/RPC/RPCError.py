class RPCDataTooLongError(AssertionError):
    """RPC调用的数据包长度过长\n
    """

    def __str__(self, *args, **kwargs):
        """
        """
        return "RPC data too long."