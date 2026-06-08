import os

# Provide harmless placeholder credentials so modules that build LLM/API
# clients can be imported during tests without real keys or network calls.
os.environ.setdefault("OPENAI_API_KEY", "sk-test")
os.environ.setdefault("COHERE_API_KEY", "test")
os.environ.setdefault("TAVILY_API_KEY", "tvly-test")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
