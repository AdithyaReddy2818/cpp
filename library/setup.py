from setuptools import setup, find_packages

setup(
    name="incident-analysis-nci",
    version="1.0.0",
    author="Adithya Reddy",
    author_email="adithya.reddy@student.ncirl.ie",
    description="Neighbourhood Safety Incident Reporting analysis library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
