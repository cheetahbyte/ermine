class Pluggable(object):
    """Baseclass for Plugins"""

    def __init__(self) -> None:
        pass

    def __call__(self, *args, **kwargs) -> None:
        return NotImplementedError()