"""
Setup script for LiteNetLib Python v0.9.5.2
LiteNetLib Python v0.9.5.2 安装脚本
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name='litenetlib-0952',
    version='1.0.0',
    description='Lite reliable UDP networking library for Python (C# LiteNetLib v0.9.5.2 compatible)',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='xiaoyanghuo',
    author_email='',
    url='https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2',
    license='MIT',
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'interop_tests', 'docs']),
    python_requires='>=3.7',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.20.0',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
    keywords='networking udp reliable protocol litenetlib game networking',
    project_urls={
        'Bug Reports': 'https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/issues',
        'Source': 'https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2',
        'Documentation': 'https://github.com/xiaoyanghuo/LiteNetLib-Python-0.9.5.2/blob/main/README.md',
    },
)
