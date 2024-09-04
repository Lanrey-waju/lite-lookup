from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="litelookup",
    version="0.2.0",
    author="Abdulmumin Akinde",
    description="A command line tool for quick concept lookups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lanrey-waju/lite-lookup",
    packages=find_packages(
        exclude=[
            "litelookup.tests",
        ],
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "groq",
        "redis",
        "pytest",
        "python-dotenv",
        "httpx[http2]",
        "prompt_toolkit",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "lookup=litelookup.main:main",
        ],
    },
)
