from service_abc import Service


class ServiceSFTP(Service):

    CHUNK_SIZE = 32767

    def __init__(self):
        pass

    def get_dirs(self):
        pass

    def chunk(self):
        pass

    def open(self):
        pass

    def connect(self):
        pass

    def create_dir(self):
        pass
