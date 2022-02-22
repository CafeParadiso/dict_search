import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dict_search",
    version="1.0.0",
    author="Cafe Paradiso",
    author_email="",
    description="Query an array of dictionaries in a style similar to mongo db",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CafeParadiso/dict_search",
    project_urls={
        "Bug Tracker": "",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)