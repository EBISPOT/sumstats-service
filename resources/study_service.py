import re
import config
from resources.error_classes import *
from resources.sqlite_client import sqlClient


class Study:
    def __init__(self, study_id, pmid, file_path, 
                 md5, assembly, callback_id=None,
                 retrieved=None, data_valid=None):
        self.study_id = study_id
        self.pmid = pmid
        self.file_path = file_path
        self.md5 = md5
        self.assembly = assembly
        self.callback_id = callback_id
        self.retrieved = retrieved
        self.data_valid = data_valid

    def valid_study_id(self):
        if re.match('^[a-zA-Z0-9]+$', self.study_id) and len(self.study_id) > 3:
            return True
        return False

    def valid_pmid(self):
        # check is alphanumeric
        return self.pmid.isalnum()

    def valid_file_path(self):
        pass

    def valid_md5(self):
        # check is alphanumeric
        return self.md5.isalnum()

    def valid_assembly(self):
        pass

    def study_id_exists_in_db(self):
        if self.get_study_from_db():
            return True
        return False

    def get_study_from_db(self):
        sq = sqlClient(config.DB_PATH)
        return sq.get_study_metadata(self.study_id)

    def create_entry_for_study(self):
        # Order here matters
        data = [self.study_id, 
                self.callback_id,
                self.pmid, 
                self.file_path, 
                self.md5, 
                self.assembly
                ]
        sq = sqlClient(config.DB_PATH)
        sq.insert_new_study(data)