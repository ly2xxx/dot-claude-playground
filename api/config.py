"""
Application configuration for the Flask API.
"""


class Config:
    """Base application configuration."""

    VERSION = "1.0.0"
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuration used during automated testing."""

    TESTING = True
