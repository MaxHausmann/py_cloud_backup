from unittest import TestCase
from py_cloud_backup.service_sftp import ServiceSFTP
from credentials import credentials as c
import pysftp
from py_cloud_backup.data import (
    File,
    Folder
)


class TestServiceSFTP(TestCase):

    def setUp(self):
        self._sftp = ServiceSFTP(c["sftp"]["host"],
                                 c["sftp"]["user"],
                                 c["sftp"]["keyfile"],
                                 c["sftp"]["keyfile_pw"],
                                 c["sftp"]["known_hosts_file"])
        self._root = c["sftp"]["root_dir"] + "py_cloud_backup_test/"

        # start second sftp service for independent testing
        cnopts = pysftp.CnOpts(knownhosts=c["sftp"]["known_hosts_file"])
        self._sftp2 = pysftp.Connection(c["sftp"]["host"],
                                        username=c["sftp"]["user"],
                                        private_key=c["sftp"]["keyfile"],
                                        private_key_pass=c["sftp"]["keyfile_pw"],
                                        cnopts=cnopts)

    def tearDown(self):
        self._sftp2.close()

    def indep_exist(self, path):
        """
        independent exists test with pysftp
        :param path: path to file
        :return: True if file exists, False if doesn't
        """
        return self._sftp2.exists(path)

    def test_exists(self):
        file_exist_path = self._root + "exist_test.txt"
        file_no_exist_path = self._root + "doesnt_test.txt"  # file doesn't exist
        folder_exist_path = self._root + "dirs_test"
        folder_no_exist_path = self._root + "doesnt_test"  # folder doesn't exist

        self.assertEqual(self.indep_exist(file_exist_path), self._sftp.exists(file_exist_path))
        self.assertEqual(self.indep_exist(file_no_exist_path), self._sftp.exists(file_no_exist_path))
        self.assertEqual(self.indep_exist(folder_exist_path), self._sftp.exists(folder_exist_path))
        self.assertEqual(self.indep_exist(folder_no_exist_path), self._sftp.exists(folder_no_exist_path))

    def test_delete(self):
        delete_path_dir = self._root+"test_dir_delete/"
        delete_path_file = self._root+"test_file_delete.txt"

        # prepare server
        self._sftp2.makedirs(delete_path_dir)  # create folder to delete
        self._sftp2.open(delete_path_file, "w").close()  # create file to delete
        self.assertTrue(self.indep_exist(delete_path_dir), "PREPARATION FAILED!")
        self.assertTrue(self.indep_exist(delete_path_file), "PREPARATION FAILED!")

        # actually test
        self._sftp.delete(delete_path_file)
        self._sftp.delete(delete_path_dir)

        self.assertFalse(self.indep_exist(delete_path_file))
        self.assertFalse(self.indep_exist(delete_path_dir))

    def test_dirs(self):
        data = self._sftp.dirs(self._root+"/dirs_test/", True)
        # files and folders are already on server and counted by me :)
        self.assertEqual(sum(isinstance(x, File) for x in data), 17)
        self.assertEqual(sum(isinstance(x, Folder) for x in data), 2)

    def test_chunk(self):
        file, content = self._sftp.chunk(self._root, "chunk_test.txt", 20, 456)
        self.assertEqual("chunk_test.txt", file.get_name())
        self.assertEqual(b'r f\xfcr Tabelle `analy', content)  # test string which is in file

    def test_file(self):
        self.fail()

    def test_create_dir(self):
        self.fail()
