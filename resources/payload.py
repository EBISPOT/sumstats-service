import os
import base64
from resources.sqlite_client import sqlClient
from resources.error_classes import *
import resources.study_service as st
import config


class Payload:
    def __init__(self, payload=None, callback_id=None):
        self.payload = payload
        self.callback_id = callback_id
        self.study_obj_list = []
        self.study_ids = []

    def get_status_for_callback_id(self):
        pass

    def get_data_for_callback_id(self):
        sq = sqlClient(config.DB_PATH)
        data = sq.get_data_from_callback_id(self.callback_id)
        if data is None:
            raise RequestedNotFound("Couldn't find resource with callback id: {}".format(self.callback_id))
        for row in data:
            study_id, callback_id, pmid, file_path, md5, assembly, retrieved, data_valid = row
            study = st.Study(study_id=study_id, callback_id=callback_id, pmid=pmid, 
                             file_path=file_path, md5=md5, 
                             assembly=assembly, retrieved=retrieved,
                             data_valid=data_valid)
            self.study_obj_list.append(study)
        return self.study_obj_list

    def check_basic_content_present(self):
        if not 'requestEntries' in self.payload:
            raise BadUserRequest("Missing 'requestEntries' in json")
        if len(self.payload['requestEntries']) == 0:
            raise BadUserRequest("Missing data")
        return True

    def create_study_obj_list(self):
        for item in self.payload['requestEntries']:
            study_id, pmid, file_path, md5, assembly = self.parse_new_study_json(item)
            study = st.Study(study_id=study_id, pmid=pmid, 
                             file_path=file_path, md5=md5, 
                             assembly=assembly)
            if not study.valid_study_id():
                raise BadUserRequest("Study ID: {} is invalid".format(study_id))
            if study.study_id_exists_in_db():
                raise BadUserRequest("Study ID: {} exists already".format(study_id))
            if study.study_id not in self.study_ids:
                self.study_ids.append(study.study_id)
                self.study_obj_list.append(study)
            else:
                raise BadUserRequest("Study ID: {} duplicated in payload".format(study_id))
        return True

    def generate_callback_id(self):
        randid = base64.b64encode(os.urandom(32))[:8]
        sq = sqlClient(config.DB_PATH)
        while sq.get_data_from_callback_id(randid) is not None:
            randid = base64.b64encode(os.urandom(32))[:8]
        self.callback_id = randid

    def set_callback_id_for_studies(self):
        self.generate_callback_id()
        for study in self.study_obj_list:
            study.callback_id = self.callback_id

    def create_entry_for_studies(self):
        for study in self.study_obj_list:
            study.create_entry_for_study()

    @staticmethod
    def parse_new_study_json(study_dict):
        """
        Expecting:
        {
           "id": "xyz321",
           "pmid": "1233454",
           "filePath": "file/path.tsv",
           "md5":"b1d7e0a58d36502d59d036a17336ddf5",
           "assembly":"38"
        }
        """
        try:
            study_id = study_dict['id']
            pmid = study_dict['pmid']
            file_path = study_dict['filePath']
            md5 = study_dict['md5']
            assembly = study_dict['assembly']
        except KeyError as e:
            raise BadUserRequest("Missing field: {} in json".format(str(e)))
        return (study_id, pmid, file_path, md5, assembly)
