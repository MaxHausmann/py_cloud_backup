class _Data:

    def __init__(self, name, path):
        self._name = name
        self._path = path

    def get_name(self):
        return self._name

    def get_path(self):
        return self._path


class File (_Data):
    def __init__(self, name, path, created, last_edit):
        super().__init__(name, path)
        self.created = created
        self.last_edit = last_edit


class Folder(_Data):
    pass
