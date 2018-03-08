from unittest import TestCase
from py_cloud_backup.service_dropbox import ServiceDropbox
from credentials import credentials as c
from os import remove
from dropbox.exceptions import (
    ApiError,
)

from py_cloud_backup.data import (
    File,
    Folder
)

TEST_FOLDER = "/py_cloud_backup_test"


class TestServiceDropbox(TestCase):

    def setUp(self):
        self._dbx = ServiceDropbox(c["dropbox"]["token"])

    def file_exists(self, path):
        try:
            self._dbx._dbx.files_get_metadata(path)
            return True
        except ApiError as e:
            if e.error.get_path().is_not_found():
                return False
            else:
                raise

    def test_delete(self):
        delete_file = TEST_FOLDER + "delete_test.txt"
        self._dbx._dbx.files_upload(b'', delete_file)  # create file to delete
        self.assertTrue(self.file_exists(delete_file), "TESTFILE DOESN'T EXIST! DELETE TEST NOT POSSIBLE.")
        self._dbx.delete(delete_file)
        self.assertFalse(self.file_exists(delete_file))

    def test_exists(self):
        exist_path = TEST_FOLDER+"/exist_test.txt"
        no_exist_path = TEST_FOLDER+"/doesnt.txt"
        self.assertEqual(self.file_exists(exist_path), self._dbx.exists(exist_path))
        self.assertEqual(self.file_exists(no_exist_path), self._dbx.exists(no_exist_path))

    def test_dirs(self):
        data = self._dbx.dirs(TEST_FOLDER+"/dirs_test/")
        # should be equal with data in test folder
        self.assertEqual(sum(isinstance(x, File) for x in data), 17)
        self.assertEqual(sum(isinstance(x, Folder) for x in data), 2)

    def test_chunk(self):
        file, content = self._dbx.chunk(TEST_FOLDER, "chunk_test.txt", 20, 456)
        self.assertEqual("chunk_test.txt", file.get_name())
        self.assertEqual(b'r f\xfcr Tabelle `analy', content)  # test string which is in file

    def test_open_file(self):
        testfile_name = "creation_test.txt"
        testfile_path = TEST_FOLDER+"/"+testfile_name
        test_payload = b'ABCDEFGHIJKLMNOP'
        with self._dbx.file(testfile_path) as f:
            f.write(test_payload)
        # file was successfully created?
        self.assertTrue(self.file_exists(testfile_path))
        self._dbx._dbx.files_download_to_file(testfile_name, testfile_path)
        with open(testfile_name, "rb") as f:
            # matching content?
            self.assertEqual(test_payload, f.read())
        # ok, delete it!
        self._dbx.delete(testfile_path)
        remove(testfile_name)

    def test_create_dir(self):
        testfolder = TEST_FOLDER+"/testfolder"
        self._dbx.create_dir(testfolder)
        self.assertTrue(self.file_exists(testfolder))
        self._dbx._dbx.files_delete_v2(testfolder)
