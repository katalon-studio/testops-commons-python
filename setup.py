import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testops-commons",
    version="1.0.0",
    author="Katalon, LLC. (https://www.katalon.com)",
    author_email="info@katalon.io",
    description="TestOps Commons Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/katalon-studio/testops-commons-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "TestOps",
        "Katalon",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
