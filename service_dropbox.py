from service_abc import Service
from dropbox import Dropbox
from contextlib import ContextDecorator

from dropbox.files import (
    FileMetadata,
    FolderMetadata,
    UploadSessionCursor,
    CommitInfo
)

from requests.sessions import session

from dropbox.exceptions import ApiError

from data import (
    File,
    Folder
)


class ServiceDropbox(Service):

    def __init__(self, access_token):
        self._access_token = access_token
        self._session = session()
        self._dbx = Dropbox(oauth2_access_token=self._access_token, session=self._session)

    def __del__(self):
        self._session.close()

    def exists(self, path):
        """
        check whether file exists or not
        :param path: file-path
        :return: True, if file exists or False if not
        :raise: ApiError on other dbx errors
        """
        try:
            self._dbx.files_get_metadata(path)
            return True
        except ApiError as e:
            if e.error.is_path and isinstance(e.error.get_path(), LookupError):
                return False
            else:
                raise

    def delete(self, path):
        self._dbx.files_delete_v2(path)

    def dirs(self, path, recursive=True):
        r = []
        for entry in self._dbx.files_list_folder(path, recursive).entries:
            if isinstance(entry, FileMetadata):
                r.append(File(entry.name, entry.path_lower, entry.client_modified, entry.client_modified))
            elif isinstance(entry, FolderMetadata):
                r.append(Folder(entry.name, entry.path_lower))
        return r

    def chunk(self, path, size, offset=0):
        p_session = session()
        dbx_p = Dropbox(oauth2_access_token=self._access_token, headers={
            "Range": "bytes=" + str(offset) + "-" + str(offset + size)}, session=p_session)  # fetch chunks from dropbox
        meta, response = dbx_p.files_download(path)
        f = File(meta.name, meta.path_lower, meta.client_modified, meta.client_modified)
        p_session.close()
        return f, response.content

    def file(self, path):
        """
        imitates open-method of python by using context-manager,
        so you can use "with" statement
        :return: interateable object
        """
        class _OpenStreamSession(ContextDecorator):
            def __init__(self, dbx):
                self._dbx = dbx
                self._data_offset = 0
                self._cur = None

            def __enter__(self):
                self._sess_id = self._dbx.files_upload_session_start(b'').session_id
                return self

            def write(self, content):
                cur = UploadSessionCursor(self._sess_id, self._data_offset)
                self._dbx.files_upload_session_append_v2(content, cur)
                self._data_offset += len(content)

            def __exit__(self, exc_type, exc_val, exc_tb):
                commit = CommitInfo(path=path, mute=True)
                cur = UploadSessionCursor(self._sess_id, self._data_offset)
                self._dbx.files_upload_session_finish(b'', cur, commit)

        return _OpenStreamSession(self._dbx)

    def create_dir(self, path):
        self._dbx.files_create_folder_v2(path)
