from py_cloud_backup.service_abc import Service

from paramiko import (
    RSAKey,
    DSSKey,
    SSHClient
)

from stat import (
    S_ISDIR,
    S_ISREG
)

from .data import (
    File,
    Folder
)

from datetime import datetime


class ServiceSFTP(Service):

    CHUNK_SIZE = 32767

    def __init__(self, host, user, private_key_file, private_key_passwd, known_hosts_file, port=22, key_type="RSA"):
        """
        Creates a new sftp connection. Currently only with auth over key-file

        :param str host: host-name (dns/ip)
        :param str user: user-name
        :param str private_key_file: path to private key file
        :param str private_key_passwd: password which protects your private key file
        :param str known_hosts_file: path to known_hosts file
        :param int port: port to server, default: 22
        :param str key_type: RSA/DSA type of your private key file
        """
        if key_type == "RSA":
            p_key = RSAKey.from_private_key_file(private_key_file, private_key_passwd)
        elif key_type == "DSA":
            p_key = DSSKey.from_private_key_file(private_key_file, private_key_passwd)

        self._ssh = SSHClient()
        self._ssh.load_host_keys(known_hosts_file)
        self._ssh.connect(hostname=host, username=user, port=port, pkey=p_key)
        self._sftp = self._ssh.open_sftp()
        #self._sftp.ssh_client = ssh  # garbage collection protection

    def __del__(self):
        self._sftp.close()
        self._ssh.close()

    def _is_dir(self, path):
        """
        checks whether path is a file or a dir

        :param str path: server-path
        :return bool: True if path is dir (false if not)
        :raises IOERROR: if dir doesn't exist
        """
        file_attr = self._sftp.stat(path)
        if S_ISDIR(file_attr.st_mode):
            return True
        else:
            return False

    def exists(self, path):
        """
        proofs whether file exists or not

        :param str path: server-path
        :return bool: True if file exists (false if not)
        """
        try:
            self._sftp.stat(path)
            return True
        except IOError:
            return False

    def delete(self, path):
        """
        delete file or folder at given path

        :param str path: server-path
        """
        if not self.exists(path):
            return

        if self._is_dir(path):
            self._sftp.rmdir(path)
        else:
            self._sftp.unlink(path)

    def dirs(self, path, recursive=True):
        """
        return all files and directories at current path

        :param str path: server-path
        :param bool recursive: run through all sub-folders
        :return: list with all files and folders as ``.data.File´´ or ``.data.Folder´´ objects
        """
        r = []

        def _recursive_runner(rec_path):
            for entry in self._sftp.listdir_attr(rec_path):
                if S_ISDIR(entry.st_mode):
                    r.append(Folder(entry.filename, rec_path))
                    if recursive:
                        _recursive_runner(rec_path+entry.filename+"/")
                elif S_ISREG(entry.st_mode):
                    time = datetime.fromtimestamp(entry.st_mtime)
                    # creation/edit time is the same time because not meaningful available yet
                    r.append(File(entry.filename, rec_path, time, time))

        _recursive_runner(path)
        return r

    def chunk(self, path, filename, size, offset=0):
        """
        returns a chunk of the target file

        :param str path: path on server
        :param str filename: name of file
        :param int size: chunk-size
        :param int offset: offset from 0
        :return: tuple(File, content)
        """
        target = path+"/"+filename
        f = self._sftp.file(target, "r")
        f.seek(offset, 0)
        r = f.read(size)
        f.close()
        stat = self._sftp.stat(target)
        time = datetime.fromtimestamp(stat.st_mtime)
        file = File(filename, path, time, time)
        return file, r

    def file(self, path):
        pass

    def create_dir(self, path):
        pass
