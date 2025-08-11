"""Utility modules for the chatbot system."""

# 순환 import 방지를 위해 필요한 것만 lazy import
# 실제 사용시에는 직접 import 권장: from utils.pdf_generator import generate_session_report

# 기본적인 유틸리티만 export
try:
    from .exceptions import (
        ChatbotError,
        AgentError,
        APIError,
        ConfigError,
        ValidationError
    )
except ImportError:
    # 의존성이 없어도 기본 동작 가능하도록
    class ChatbotError(Exception): pass
    class AgentError(Exception): pass
    class APIError(Exception): pass
    class ConfigError(Exception): pass
    class ValidationError(Exception): pass

# 기본 로깅 설정은 항상 가능하도록
try:
    from .logging_config import setup_logging, get_logger
except ImportError:
    import logging
    def setup_logging(): return logging.getLogger()
    def get_logger(name): return logging.getLogger(name)

__all__ = [
    # Exceptions
    'ChatbotError',
    'AgentError', 
    'APIError',
    'ConfigError',
    'ValidationError',
    
    # Logging
    'setup_logging',
    'get_logger'
]
