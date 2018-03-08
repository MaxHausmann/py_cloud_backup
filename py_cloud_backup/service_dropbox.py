from py_cloud_backup.service_abc import Service
from dropbox import Dropbox
from contextlib import ContextDecorator

from dropbox.files import (
    FileMetadata,
    FolderMetadata,
    UploadSessionCursor,
    CommitInfo
)

from requests.sessions import session

from dropbox.exceptions import (
    ApiError
)

from py_cloud_backup.data import (
    File,
    Folder
)


class ServiceDropbox(Service):

    def __init__(self, access_token):
        """
        starts a new connection to dropbox

        :param str access_token: dbx access token
        """
        self._access_token = access_token
        self._session = session()
        self._dbx = Dropbox(oauth2_access_token=self._access_token, session=self._session)

    def __del__(self):
        self._session.close()

    def exists(self, path):
        """
        check whether file exists or not
        :param str path: file_path
        :return bool : True, if file exists or False if not
        :raise: ApiError on other dbx errors
        """
        try:
            self._dbx.files_get_metadata(path)
            return True
        except ApiError as e:
            if e.error.get_path().is_not_found():
                return False
            else:
                raise

    def delete(self, path):
        """
        delete some dir or file

        :param str path: path to delete
        """
        self._dbx.files_delete_v2(path)

    def dirs(self, path, recursive=True):
        """
        return files and dirs in current folder

        :param str path: current folder
        :param bool recursive: go deeper?
        :return: list with files/dirs
        """
        r = []
        for entry in self._dbx.files_list_folder(path, recursive).entries:
            file_name_len = len(entry.name)
            if path.split("/")[-2] == entry.name:
                continue
            if isinstance(entry, FileMetadata):
                r.append(File(entry.name, entry.path_lower[0:-file_name_len].lstrip("/"), entry.client_modified, entry.client_modified))
            elif isinstance(entry, FolderMetadata):
                r.append(Folder(entry.name, entry.path_lower[0:-file_name_len].lstrip("/")))
        return r

    def chunk(self, path, filename, size, offset=0):
        """
        return one chunk of file

        :param str path: path on server
        :param str filename: name of file
        :param int size: chunk-size
        :param int offset: bits from the beginning
        :return: tuple(File obj, content)
        """
        p_session = session()
        dbx_p = Dropbox(oauth2_access_token=self._access_token, headers={
            "Range": "bytes=" + str(offset) + "-" + str(offset + size - 1)}, session=p_session)  # fetch chunks from dropbox
        meta, response = dbx_p.files_download(path+"/"+filename)
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
        """
        create dir at specific location

        :param path: location to create dir
        """
        self._dbx.files_create_folder_v2(path)
