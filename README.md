# Retrieval-Augmented Generation (RAG) Database Preprocessor
This project builds a vector database leveraging ChromaDB as a component of a Retrieval-Augmented Generation (RAG)-based chatbot/agent.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Installation
In keeping with recommended best practices (see PEP 517, 518, and 621), the project leverages the pyproject.toml Python Packaging that has replaced setuptools as the modern approach to packaging. Follow the three steps below:

1. create a virtual environment by runnning `python -m venv .venv`
2. install all required dependencies by running `pip install .`, which will leverage *pyproject.toml* to build everything.
3. As discovered in [this issue](https://github.com/microsoft/autogen/issues/251), we fix a dependency problem related to sqlite3 by installing `pysqlite3-binary`. (last update: then, you need to create in your venv's "lib/python3.12/site-packages/google" folder a new folder called 'collab' but might not be required now... further testing may be needed as well).

## Usage

## Contributing
1. Create an issue where we can chat about your idea(s)
2. Once approved, fork the repo and create a Pull Request
3. We'll do some code review and merge into main if everything looks good

