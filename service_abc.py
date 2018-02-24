from abc import ABC


class Service(ABC):

    @classmethod
    def exists(cls, path):
        pass

    @classmethod
    def delete(cls, path):
        pass

    @classmethod
    def dirs(cls, path, recursive=True):
        pass

    @classmethod
    def chunk(cls, path, size, offset=0):
        pass

    @classmethod
    def file(cls, path):
        pass

    @classmethod
    def create_dir(cls, path):
        pass
