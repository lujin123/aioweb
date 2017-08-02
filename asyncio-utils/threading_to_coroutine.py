# Created by lujin at 1/8/2017
"""
将同步的函数转换成异步函数

通过将同步阻塞的函数的调用放到线程中执行，从而不会对主线程造成阻塞，
然后将执行完的结果通过future来传递给EventLoop，这样就可以从future中拿到阻塞函数中的结果了

在asyncio库中有个类似的函数run_in_executor，就是用来执行一个阻塞调用的，默认使用的线程池（ThreadPoolExecutor）

"""
import asyncio
import threading

import time
import functools


def coroutine(func):
    """
    将同步阻塞函数转换成协程调用的装饰器

    被装饰后就可以跟协程一样调用

    ``` py
    @coroutine
    def fetch():
        time.sleep(5)
        return 'set future result...'

    async index():
        res = await fetch()

    ```
    :param func: 被装饰的同步函数
    :return:
    """
    @functools.wraps(func)
    async def _wrapper():
        future = asyncio.Future()
        # 没有对异常进行处理,只是简单的将阻塞函数获取到的结果塞到future的结果中，这里可以使用线程池替代
        thread = threading.Thread(target=lambda f: f.set_result(func()), args=(future, ))
        thread.start()
        res = await future
        return res
    return _wrapper


@coroutine
def fetch():
    print('fetch something...')
    time.sleep(5)
    return 'set future result...'


@asyncio.coroutine
def index():
    res = yield from fetch()
    print('index result: ', res)


async def index2():
    res = await fetch()
    print('index2 result: ', res)

async def print_forever():
    while True:
        print('hello world...')
        await asyncio.sleep(1)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*[index(), print_forever(), index2()]))
    loop.close()

if __name__ == '__main__':
    main()
