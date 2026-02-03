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

setup(
    name='litenetlib',
    version='1.0.0',
    description='Lite reliable UDP networking library for Python (v0.9.5.2 compatible)',
    long_description=readme_readme(),
    long_description_content_type='text/markdown',
    author='xiaoyanghuo',
    author_email='',
    url='https://github.com/xiaoyanghuo/LiteNetLib-Python',
    license='MIT',
    packages=find_packages(),
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
    ],
    keywords='networking udp reliable protocol litenetlib',
    project_urls={
        'Bug Reports': 'https://github.com/xiaoyanghuo/LiteNetLib-Python/issues',
        'Source': 'https://github.com/xiaoyanghuo/LiteNetLib-Python',
    },
)
