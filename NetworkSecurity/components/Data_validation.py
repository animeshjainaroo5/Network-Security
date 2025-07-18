from NetworkSecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from NetworkSecurity.entity.config_entity import DataValidationConfig
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from NetworkSecurity.logging.logger import logging
from scipy.stats import ks_2samp
import pandas as pd
import os, sys
from NetworkSecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

class DataValidation:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,
                 data_validation_config:DataValidationConfig):
        
        try:
            self.data_ingestion_artifact=data_ingestion_artifact
            self.data_validation_config=data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        

    def validate_no_of_col(self, dataframe:pd.DataFrame)-> bool:
        try: 
            no_of_col = len(self._schema_config)
            logging.info(f"Required number of cols: {no_of_col}")
            logging.info(f"Data frame has columns: {len(dataframe.columns)}")
            if len(dataframe.columns) == no_of_col:
                return True
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    
    def detect_drift(self, base_df, current_df, threshold=0.5)->bool:
        try: 
            status=True
            report={}
            for column in base_df.columns:
                d1 = base_df[column]
                d2  =current_df[column]
                is_sample_dist = ks_2samp(d1, d2)

            if threshold<=is_sample_dist.pvalue:
                is_found=False
            else:
                is_found =True
                status=False
                report.update({column:{
                    "p_value":float(is_sample_dist.pvalue),
                    "drift_status":is_found
                }})
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def initiate_data_validation(self)-> DataValidationArtifact:
        try:
            train_file_path  =self.data_ingestion_artifact.trained_file_path
            test_file_path  =self.data_ingestion_artifact.test_file_path
            
            #read the data from train and test
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe = DataValidation.read_data(test_file_path)

            #validte no of cols
            status = self.validate_no_of_col(dataframe=train_dataframe)
            if not status:
                error_message=f"Train Dataframe does not contain all the columns. \n"
            status = self.validate_no_of_col(dataframe=test_dataframe)
            if not status:
                error_message=f"Test Dataframe does not contain all the columns. \n"

            #lets check datadrift
            status = self.detect_drift(base_df=train_dataframe, current_df=test_dataframe)
            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )

            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_ingestion_artifact.trained_file_path,
                valid_test_file_path=self.data_ingestion_artifact.test_file_path,
                invalid_train_file_path=None,
                invalid_test_file_path=None,
                drift_report_file_path=self.data_validation_config.drift_report_file_path,
            )
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)
