from setuptools import setup, find_packages

setup(
    name="database_client",
    version="0.1.0",
    author="Erik",
    author_email="null",
    description="A Python library for interacting with various databases.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/ErikDevelopment/database_client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'mariadb',
        'psycopg2'
    ],
)
