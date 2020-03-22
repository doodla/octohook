import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="octohook",
    version="0.1",
    author="Sridhar Vadlamani",
    author_email="v.sridhar.sreenivas@gmail.com",
    description="Typed interactions with Github Webhooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/doodla/octohook",
    packages=["octohook"],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
)
