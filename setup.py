"""Setup script for IDFW - IDEA Definition Framework."""

from setuptools import setup, find_packages

setup(
    name="idfw",
    version="1.0.0",
    description="IDFW - IDEA Definition Framework: Unified schema, agent orchestration, FORCE governance, and MCP integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Jeremiah Pegues",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.108.0",
        "uvicorn[standard]>=0.25.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "click>=8.1.7",
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "jsonschema>=4.20.0",
        "pyyaml>=6.0.1",
        "python-dotenv>=1.0.0",
        "msgpack>=1.0.7",
        "websockets>=12.0",
        "sqlalchemy>=2.0.25",
        "alembic>=1.13.1",
        "httpx>=0.26.0",
        "aiohttp>=3.9.1",
        "mcp>=0.5.0",
        "python-multipart>=0.0.6",
    ],
    entry_points={
        "console_scripts": [
            "idfw=unified_framework.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
