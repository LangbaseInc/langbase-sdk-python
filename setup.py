"""
Setup script for the Langbase SDK.
"""
from setuptools import setup, find_packages

# Set version directly without trying to import it
VERSION = "0.1.0"

# Read the contents of the README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="langbase",
    version=VERSION,
    description="Python SDK for the Langbase API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Langbase",
    author_email="support@langbase.com",
    url="https://github.com/langbaseinc/langbase-sdk-python",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords="ai, langbase, llm, embeddings, vector store",
    project_urls={
        "Documentation": "https://docs.langbase.com",
        "Source": "https://github.com/langbaseinc/langbase-sdk-python",
        "Issues": "https://github.com/langbaseinc/langbase-sdk-python/issues",
    },
)
