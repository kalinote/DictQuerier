"""
JsonQuerier 安装配置
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="JsonQuerier",
    version="0.1.0",
    author="kalinote",
    author_email="knote840746219@gmail.com",
    description="基于路径的Json数据查询工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kalinote/JSONQuerier",
    project_urls={
        "Bug Tracker": "https://github.com/kalinote/JSONQuerier/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    keywords="json, query, path, jsonpath, json-path",
    entry_points={
        'console_scripts': [
            'jsonquerier=jsonquerier.cli:main',
        ],
    },
) 