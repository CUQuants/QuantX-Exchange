from setuptools import setup, find_packages

setup(
    name="quantx_exchange_client",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "websockets",
    ],
    author="QuantX",
    author_email="contact@quantx.com",
    description="A client library for interacting with the QuantX Exchange API.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/QuantX-Exchange",  # Replace with your repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
