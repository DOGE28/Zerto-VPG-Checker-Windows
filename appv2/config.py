from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    keycloak_client_id: str
    sgu_prod_zvm_url: str
    sgu_prod_secret: str
    boi_prod_zvm_url: str
    boi_prod_secret: str
    fb_prod_zvm_url: str
    fb_prod_secret: str
    sgu_inf_zvm_url: str
    sgu_inf_secret: str
    boi_inf_zvm_url: str
    boi_inf_secret: str
    okc_inf_zvm_url: str
    okc_inf_secret: str
    class Config:
        env_file = '../.env'
settings = Settings()