from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="litelookup",
    version="0.1.1",
    author="Abdulmumin Akinde",
    description="A command line tool for quick concept lookups",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lanrey-waju/litelookup",
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
    intall_requires=[
        "groq",
        "pytest",
        "python-dotenv",
        "redis",
    ],
    entry_points={
        "console_scripts": [
            "lookup=litelookup.main:main",
        ],
    },
)
