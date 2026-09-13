from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Buy or Wait?"
    app_version: str = "2.0.0"
    debug: bool = True

    database_url: str = "postgresql://postgres:password@localhost:5432/buy_or_wait"

    # ---------------------------------------------------------------
    # Auth / JWT (login credentials)
    # ---------------------------------------------------------------
    jwt_secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # ---------------------------------------------------------------
    # LLM / Agentic AI (Groq)
    # ---------------------------------------------------------------
    # The affordability decision is produced entirely by an LLM agent
    # (see app/services/ai_service.py) that calls tools to inspect the
    # user's real financial data. There is no hard-coded rule engine
    # deciding the final recommendation any more.
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"
    agent_max_tool_turns: int = 6

    # CORS
    frontend_origin: str = "http://localhost:5173"

    class Config:
        env_file = ".env"


settings = Settings()
