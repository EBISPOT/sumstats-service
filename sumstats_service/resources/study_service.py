import re
import config
from sumstats_service.resources.error_classes import *
from sumstats_service.resources.sqlite_client import sqlClient
import sumstats_service.resources.file_handler as fh


class Study:
    def __init__(self, study_id, file_path,
                 md5, assembly, callback_id=None,
                 retrieved=None, data_valid=None,
                 status=None, error_code=None):
        self.study_id = study_id
        self.file_path = file_path
        self.md5 = md5
        self.assembly = assembly
        self.callback_id = callback_id
        self.retrieved = retrieved
        self.data_valid = data_valid
        self.error_code = error_code


    def valid_study_id(self):
        if re.match('^[a-zA-Z0-9]+$', self.study_id) and len(self.study_id) > 3:
            return True
        return False

    def get_status(self):
        if self.retrieved is None:
           status = 'RETRIEVING'
        if self.retrieved is 1 and self.data_valid is None:
            status = 'VALIDATING'
        if self.retrieved is 0 or self.data_valid is 0:
            status = 'INVALID'
        if self.retrieved is 1 and self.data_valid is 1:
            status = 'VALID'
        return status

    @staticmethod
    def get_error_report():
        return None

    def update_retrieved_status(self, status):
        self.retrieved = status
        sq = sqlClient(config.DB_PATH)
        sq.update_retrieved_status(self.study_id, status)

    def update_data_valid_status(self, status):
        self.data_valid = status
        sq = sqlClient(config.DB_PATH)
        sq.update_data_valid_status(self.study_id, status)


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
        study_metadata = sq.get_study_metadata(self.study_id)
        if study_metadata:
            self.study_id, self.callback_id, self.file_path, self.md5, self.assembly, self.retrieved, self.data_valid, self.error_code = study_metadata
        return study_metadata

    def create_entry_for_study(self):
        # Order here matters
        data = [self.study_id,
                self.callback_id,
                self.file_path,
                self.md5,
                self.assembly
                ]
        sq = sqlClient(config.DB_PATH)
        sq.insert_new_study(data)

    def study_to_validation_queue(self):
        ssf = fh.SumStatFile(file_path=self.file_path, callback_id=self.callback_id,
                study_id=self.study_id, md5exp=self.md5)
        if ssf.retrieve() is True:
            self.update_retrieved_status(1)
            if not ssf.md5_ok():
                self.update_data_valid_status(0)
        if ssf.retrieve() is False:
            self.update_retrieved_status(0)
        
        
    
        
