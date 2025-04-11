from setuptools import setup, find_packages

setup(
    name="medical_chatbot",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "spacy>=3.7.2",
        "sentence-transformers>=2.2.2",
        "neo4j>=5.14.1",
        "qdrant-client>=1.6.4",
        "pymongo>=4.6.1",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
) 