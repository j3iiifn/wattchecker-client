#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gzip
import shutil
import os
import threading

import logging_util
logger = logging_util.get_logger(__name__)

class DataHandler:
    def __init__(self, config):
        if config.get('bigquery'):
            if config['bigquery'].get('service_account_json') and config['bigquery'].get('dataset_id') and config['bigquery'].get('table_id'):
                self.bigquery_service_account_json = config['bigquery']['service_account_json']
                self.bigquery_dataset_id = config['bigquery']['dataset_id']
                self.bigquery_table_id = config['bigquery']['table_id']

    def _upload_csv_to_bigquery(self, filename):
        from google.cloud import bigquery

        try:
            client = bigquery.Client.from_service_account_json(self.bigquery_service_account_json)
            dataset_ref = client.dataset(self.bigquery_dataset_id)
            table_ref = dataset_ref.table(self.bigquery_table_id)

            job_config = bigquery.LoadJobConfig()
            job_config.source_format = bigquery.SourceFormat.CSV
            job_config.skip_leading_rows = 0
            job_config.autodetect = False
            job_config.schema = [
                bigquery.SchemaField("datetime", "DATETIME"),
                bigquery.SchemaField("V", "FLOAT"),
                bigquery.SchemaField("mA", "FLOAT"),
                bigquery.SchemaField("W", "FLOAT")
            ]

            with open(filename, "rb") as source_file:
                job = client.load_table_from_file(
                    source_file,
                    table_ref,
                    location="asia-northeast1",
                    job_config=job_config,
                )

            job.result()

            logger.info("Loaded {} rows into {}:{}.".format(job.output_rows, self.bigquery_dataset_id, self.bigquery_table_id))
        except Exception as e:
            logger.warning('an unexpected error has occurred in _upload_csv_to_bigquery. %s' % e)

    def _gzip_file(self, source, destination):
        with open(source, 'rb') as f_in:
            with gzip.open(destination, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        os.remove(source)

    def data_logger_namer(self, name):
        return name + ".gz"

    def data_logger_rotator(self, source, destination):
        self._gzip_file(source, destination)

        if self.bigquery_service_account_json:
            thread = threading.Thread(target=self._upload_csv_to_bigquery, args=[destination])
            thread.start()
