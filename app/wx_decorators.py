import functools

import wx


def wx_call_after(target):
    @functools.wraps(target)
    def wrapper(self, *args, **kwargs):
        args = (self,) + args
        wx.CallAfter(target, *args, **kwargs)

    return wrapper


def submit_to_pool_executor(executor):
    """Decorates a method to be submitted to the passed in executor"""

    def decorator(target):
        @functools.wraps(target)
        def wrapper(*args, **kwargs):
            result = executor.submit(target, *args, **kwargs)
            result.add_done_callback(executor_done_call_back)
            return result

        return wrapper

    return decorator


def executor_done_call_back(future):
    exception = future.exception()
    if exception:
        raise exception
