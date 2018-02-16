from abc import ABC, abstractmethod


class CloudService(ABC):

    def __init__(self):
        pass

    def get_dirs(self):
        pass

    def get_chunk(self):
        pass

    def open(self):
        pass

    def connect(self):
        pass

    def create_dir(self):
        pass

    def test(self):
        pass


