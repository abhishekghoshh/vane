"""Singleton metaclass for creating singleton classes."""

import logging
from abc import ABCMeta

logger = logging.getLogger("uvicorn")


class Singleton(ABCMeta):
    """A metaclass for creating singleton classes."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
