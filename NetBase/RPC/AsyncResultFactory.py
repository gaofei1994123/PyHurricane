from gevent.event import AsyncResult
import hashlib
import gevent

'''
生成唯一的键值字符串
'''
def makeUniqueKey(result):
    md = hashlib.md5()
    key = str(id(result))
    md.update(bytes(key, 'utf-8'))
    key_last = md.hexdigest()
    return key_last

'''
异步工厂
'''
class AsyncResultFactory():
    '''
    静态变量，存储 key 对应的 异步调用方法
    '''
    __async_results = {}

    def createAsyncResult(self):
        result = AsyncResult()
        key = makeUniqueKey(result)
        AsyncResultFactory.__async_results[key] = result
        return key, result

    def dropAsyncResultBykey(self, key):
        if key in AsyncResultFactory.__async_results:
            del AsyncResultFactory.__async_results[key]

    def popAsyncResult(self, key):
        if key in AsyncResultFactory.__async_results:
            a = AsyncResultFactory.__async_results.get(key)
            del AsyncResultFactory.__async_results[key]
            return a
        else:
            return None