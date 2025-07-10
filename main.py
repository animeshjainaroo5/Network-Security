from NetworkSecurity.components.data_ingestion import DataIngestion
from NetworkSecurity.components.Data_validation import DataValidation
import sys
from NetworkSecurity.exception.exception import NetworkSecurityException
from NetworkSecurity.logging.logger import logging
from NetworkSecurity.entity.config_entity import DataIngestionConfig, DataValidationConfig, DataTransformationConfig
from NetworkSecurity.entity.config_entity import TrainingPipelineConfig
from NetworkSecurity.components.data_transformation import DataTransformation

if __name__=='__main__':
    try:
        trainingpipelineconfig= TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)
        logging.info("Data Ingestion initiated")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Ingestion Completed")
        print(dataingestionartifact)
        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(dataingestionartifact, data_validation_config)
        logging.info("Initiate the data Validation")
        data_validation_artifact  =data_validation.initiate_data_validation()
        logging.info("Completed the data Validation")
        print(data_validation_artifact)
        data_transformation_config = DataTransformationConfig(trainingpipelineconfig)
        logging.info("Initiate the data transformation")
        data_transformation = DataTransformation(data_validation_artifact, data_transformation_config)
        logging.info("Completed the data transformation")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        print(data_transformation_artifact)


    except Exception as e:
           raise NetworkSecurityException(e,sys) 