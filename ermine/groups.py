from ermine.plugs.routable import Routable


class Group(Routable):
    def __init__(self, prefix: str = None) -> None:
        super().__init__()
        self.prefix = prefix