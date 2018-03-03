from service_abc import Service


class ServiceSFTP(Service):

    CHUNK_SIZE = 32767

    def __init__(self):
        pass

    def exists(self, path):
        pass
    
    def delete(self, path):
        pass

    def dirs(self, path, recursive=True):
        pass

    def chunk(self, path, size, offset=0):
        pass

    def file(self, path):
        pass

    def create_dir(self, path):
        pass
