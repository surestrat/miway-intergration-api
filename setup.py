from setuptools import setup, find_packages

setup(
    name="miway-integration-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "appwrite",
        "pydantic-settings",
        "python-multipart",
        "uvicorn",
        "jinja2",
        "python-dotenv",
        "redis",
        "httpx",
        "email-validator",
    ],
    python_requires=">=3.11",
)
