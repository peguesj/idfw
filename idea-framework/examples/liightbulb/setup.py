from setuptools import setup, find_packages

setup(
    name='liightbulb',
    version='0.4.2',
    description='A command-line interpreter for the IDEA framework using OpenAI API',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'openai',
    ],
    entry_points={
        'console_scripts': [
            'idfw=liightbulb.idfw:main',
        ],
    },
)
