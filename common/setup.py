import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CloudBotWorkersCommon",
    version="0.0.1",
    author="Akhilesh Halageri",
    author_email="akhilesh@zetta.ai",
    description="Common definitions and utils for use in workers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZettaAI/cloud-bot-workers/common",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
)