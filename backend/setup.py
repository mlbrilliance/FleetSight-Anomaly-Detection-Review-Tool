"""
Setup script for the backend package.
"""

from setuptools import setup, find_packages

setup(
    name="fleetsight-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "supabase>=2.0.0",
        "python-jose>=3.3.0",
        "email-validator>=2.0.0",
    ],
) 