# Labour Program's Internal Chatbot's Vector Database
This project builds a vector database leveraging ChromaDB to support the Labour Program's Internal Chatbot as a component of its Retrieval-Augmented Generation (RAG) architecture.

**N.B.: The src layout requires installation of the project to be able to run its code. In keeping with recommended best practices (see PEP 517, 518, and 621), the project leverages the pyproject.toml Python Packaging that has replaced setuptools as the modern approach to packaging. Please run `pip install .`before running anything else.**

> As discovered in [this issue](https://github.com/microsoft/autogen/issues/251), we fix a dependency problem related to sqlite3 by running by installing `pysqlite3-binary` instead. (last update: then needed creating in your venv's "lib/python3.12/site-packages/google" folder a new folder called 'collab' but might not be required now)