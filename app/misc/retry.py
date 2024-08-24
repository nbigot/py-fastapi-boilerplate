# -*- coding: utf-8 -*-
# pylint: disable=W0718,R1710

import logging
import random
import time

logging_logger = logging.getLogger(__name__)


def __retry_internal(
    f,
    fargs=None,
    fkwargs=None,
    exceptions=Exception,
    tries=-1,
    delay=0,
    max_delay=None,
    backoff=1,
    jitter=0,
    logger=logging_logger,
    f_ex_callback=None,
):
    """
    Executes a function and retries it if it failed.

    :param f: the function to execute.
    :param fargs: the arguments to pass to the function
    :param fkwargs: the dict arguments to pass to the function
    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logging_logger. if None, logging is disabled.
    :param f_ex_callback: a callback function to handle exception.
    :returns: the result of the f function.
    """
    _tries, _delay = tries, delay
    while _tries:
        try:
            args = fargs if fargs else []
            kwargs = fkwargs if fkwargs else {}
            return f(*args, **kwargs)
        except exceptions as ex:
            _tries -= 1
            if not _tries:
                raise

            if f_ex_callback:
                f_ex_callback(*args, **kwargs, _ex=ex, _tries=_tries)

            if logger is not None:
                logger.warning("%s, retrying in %s seconds...", ex, _delay)

            time.sleep(_delay)
            _delay *= backoff

            if isinstance(jitter, tuple):
                _delay += random.uniform(*jitter)
            else:
                _delay += jitter

            if max_delay is not None:
                _delay = min(_delay, max_delay)


def retry(
    exceptions=Exception,
    tries=-1,
    delay=0,
    max_delay=None,
    backoff=1,
    jitter=0,
    logger=logging_logger,
    f_ex_callback=None,
):
    """Returns a retry decorator.

    :param exceptions: an exception or a tuple of exceptions to catch. default: Exception.
    :param tries: the maximum number of attempts. default: -1 (infinite).
    :param delay: initial delay between attempts. default: 0.
    :param max_delay: the maximum value of delay. default: None (no limit).
    :param backoff: multiplier applied to delay between attempts. default: 1 (no backoff).
    :param jitter: extra seconds added to delay between attempts. default: 0.
                   fixed if a number, random if a range tuple (min, max)
    :param logger: logger.warning(fmt, error, delay) will be called on failed attempts.
                   default: retry.logging_logger. if None, logging is disabled.
    :param f_ex_callback: a callback function to handle exception.
    :returns: a retry decorator.
    """

    def retry_decorator(func):
        def new_func(*args, **kwargs):
            return __retry_internal(
                func,
                args,
                kwargs,
                exceptions,
                tries,
                delay,
                max_delay,
                backoff,
                jitter,
                logger,
                f_ex_callback,
            )

        return new_func

    return retry_decorator
