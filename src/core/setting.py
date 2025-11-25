from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
    )

    project_name: str = Field(
        default="interview-service",
        description="Project name",
        alias="PROJECT_NAME",
        validation_alias="PROJECT_NAME",
    )
    project_version: str = Field(
        default="0.1.0",
        description="Project version",
        alias="PROJECT_VERSION",
        validation_alias="PROJECT_VERSION",
    )
    project_description: str = Field(
        default="Interview Service manage room interview sessions",
        description="Project description",
        alias="PROJECT_DESCRIPTION",
        validation_alias="PROJECT_DESCRIPTION",
    )
    public_key: str = Field(
        default="public_key",
        description="Public key",
        alias="PUBLIC_KEY",
        validation_alias="PUBLIC_KEY",
    )

    llm_max_tokens: int = Field(
        default=25_000,
        description="LLM maximum tokens",
        alias="LLM_MAX_TOKENS",
        validation_alias="LLM_MAX_TOKENS",
    )

    llm_model: str = Field(
        default="qwen3-32b-awq",
        description="LLM model",
        alias="LLM_MODEL_NAME",
        validation_alias="LLM_MODEL_NAME",
    )

    openai_base_url: str = Field(
        default="https://llm.t1v.scibox.tech/v1",
        description="OpenAI base URL",
        alias="OPENAI_BASE_URL",
        validation_alias="OPENAI_BASE_URL",
    )

    openai_api_key: str = Field(
        default="",
        description="OpenAI API key",
        alias="OPENAI_API_KEY",
        validation_alias="OPENAI_API_KEY",
    )


settings = Settings()
