import abc


class IoDeSerable:
    @staticmethod
    @abc.abstractmethod
    def __io__() -> dict:
        pass
