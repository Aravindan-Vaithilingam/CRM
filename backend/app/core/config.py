from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = 'CRM Project Approval API'
    PROJECT_VERSION: str = '0.1.0'

    DATABASE_URL: str = 'postgresql+psycopg2://postgres:postgres@localhost:5432/crm'
    AWS_REGION: str = 'us-east-1'
    S3_BUCKET: str = 'crm-project-contracts'
    STORAGE_MODE: str = 'local'
    class Config:
        env_file = '.env'
        case_sensitive = True
settings = Settings()
