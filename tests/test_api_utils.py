import unittest
import os
import config
from tests.test_constants import *
import resources.api_utils as au
from resources.error_classes import *
from resources.sqlite_client import sqlClient


class TestAPIUtils(unittest.TestCase):
    def setUp(self):
        self.testDB = "./tests/study_meta.db"
        config.DB_PATH = self.testDB 
        sq = sqlClient(self.testDB)
        sq.create_conn()
        sq.cur.execute(config.DB_SCHEMA)


    def tearDown(self):
        os.remove(self.testDB)



if __name__ == '__main__':
    unittest.main()