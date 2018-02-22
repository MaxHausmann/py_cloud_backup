from abc import ABC


class Service(ABC):

    @classmethod
    def dirs(cls, target, recursive):
        pass

    @classmethod
    def chunk(cls, target, size, offset=0):
        pass

    @classmethod
    def file(cls, path):
        pass

    @classmethod
    def create_dir(cls, path):
        pass
