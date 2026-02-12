"""Agent configuration for OpenAI Agents SDK."""
from pydantic_settings import BaseSettings
from typing import Optional


class AgentConfig(BaseSettings):
    """Configuration for the AI agent.

    Attributes:
        model: OpenAI model to use (gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo)
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
        timeout: Request timeout in seconds
    """

    model: str = "arcee-ai/trinity-large-preview:free"
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout: int = 30

    class Config:
        env_prefix = "AGENT_"


# Default agent configuration
agent_config = AgentConfig()
