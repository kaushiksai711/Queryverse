from setuptools import setup, find_packages

setup(
    name="medical-chatbot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "neo4j",
        "qdrant-client",
        "sentence-transformers",
        "tqdm",
        "numpy",
    ],
) 