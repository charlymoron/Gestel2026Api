# ======================================================================================
# CONFIGURACIÓN
# ======================================================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Base de datos
    DATABASE_URL: str = (

    )

    # Carpetas
    TRAPS_FOLDER: str = "./Traps"
    OUTPUT_FOLDER: str = "./Output"

    # Configuración de procesamiento
    DEFAULT_OPERATOR_ID: int = 1
    BATCH_SIZE: int = 1000

    # Tipos de evento
    EVENTO_DOWN: int = 1
    EVENTO_UP: int = 2

    # Tipo de identificador IP
    TIPO_IDENTIFICADOR_IP: int = 2

    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
