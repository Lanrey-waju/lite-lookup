from pathlib import Path
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r") as req_file:
    dependencies = []
    lines = req_file.readlines()
    for line in lines:
        line = line.strip("\n")
        dependencies.append(line)

here = Path(__file__).resolve().parent
VERSION = (here / "VERSION").read_text(encoding="utf-8").strip()

setup(
    name="litelookup",
    version=VERSION,
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
    # package_data={"litelookup": ["log/*.json"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=dependencies,
    entry_points={
        "console_scripts": [
            "lookup=litelookup.main:main",
        ],
    },
)
