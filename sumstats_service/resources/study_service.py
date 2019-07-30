import re
import config
from sumstats_service.resources.error_classes import *
from sumstats_service.resources.sqlite_client import sqlClient
import sumstats_service.resources.file_handler as fh
import pika


class Study:
    def __init__(self, study_id, file_path,
                 md5, assembly, callback_id=None,
                 retrieved=None, data_valid=None,
                 status=None):
        self.study_id = study_id
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

    def get_status(self):
        if self.retrieved is None:
           status = 'VALIDATING'
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
            self.study_id, self.callback_id, self.file_path, self.md5, self.assembly, self.retrieved, self.data_valid = study_metadata
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
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=config.RABBITMQ_HOST, port=config.RABBITMQ_PORT))
        channel = connection.channel()
        
        channel.queue_declare(queue='task_queue', durable=True)
        
        message = str(self.study_id)
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))
        print(" [x] Sent %r" % message)
        connection.close()
