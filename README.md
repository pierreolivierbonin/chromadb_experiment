# Retrieval-Augmented Generation (RAG) Database Preprocessor
This project helps you preprocess data to build a vector database leveraging ChromaDB for use cases like Retrieval-Augmented Generation (RAG)-based chatbots/agents.

## Built With
* [Chroma](https://www.trychroma.com/)
* [SentenceTransformers](https://sbert.net/)

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Installation
In keeping with recommended best practices (see PEP 517, 518, and 621), the project leverages the pyproject.toml Python Packaging that has replaced setuptools as the modern approach to packaging. 

Follow the three steps below:

0. *(optional)* install [`uv`](https://github.com/astral-sh/uv) by running `pip install uv` to use the fastest Python package and project manager.
1. create a virtual environment by runnning `python -m venv .venv`
2. activate the newly-created venv by running `./.venv/scripts/activate`
3. install all required dependencies by running `uv pip install .` This will leverage *pyproject.toml* to build everything.

## Usage
Use the modules included in src/utils to preprocess your documents. For example:
* if you have .docx documents, use `docx_processor.py` to transform your Word documents to plain text format files (.txt);
* if you want to parse HTML tables, use `htmltables_converter.py` to transform them into dataframes and save the output into .csv files. 
> See *scripts/IPGs_example.py* for an example, which uses *HTMLTablestoDataframes* to output a clean dataframe from an HTML table found on a webpage.

> See *create_database_with_specific_embeddings.py* for an example on how to use the `chromadb` and `sentence-transformers` libraries to create embeddings, and then save a local vector database that you can reuse in any of your use cases.

## Contributing
1. Create an issue where we can chat about your idea(s)
2. Fork the repo and create a Pull Request once you have something you think is ready to merge.
3. We'll do some code review and merge into main if everything looks good

