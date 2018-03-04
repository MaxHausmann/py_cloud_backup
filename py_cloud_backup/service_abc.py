from abc import ABC


class Service(ABC):

    @classmethod
    def exists(cls, path):
        raise NotImplementedError("Method must be implemented!")

    @classmethod
    def delete(cls, path):
        raise NotImplementedError("Method must be implemented!")

    @classmethod
    def dirs(cls, path, recursive=True):
        raise NotImplementedError("Method must be implemented!")

    @classmethod
    def chunk(cls, path, size, offset=0):
        raise NotImplementedError("Method must be implemented!")

    @classmethod
    def file(cls, path):
        raise NotImplementedError("Method must be implemented!")

    @classmethod
    def create_dir(cls, path):
        raise NotImplementedError("Method must be implemented!")
