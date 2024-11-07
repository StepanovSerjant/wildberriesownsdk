from os.path import join, dirname
from setuptools import setup, find_packages

__version__ = "0.0.1"
with open("requirements.txt") as f:
    requirements = f.read().splitlines()


setup(
    name="wildberriesapi",
    version=__version__,
    description="Wildberries API SDK. (not official)",
    long_description=open(join(dirname(__file__), "README.md")).read(),
    url="https://github.com/StepanovSerjant/wildberriesownsdk",
    author="Aleksey Stepanov",
    author_email="stpnvlks@gmail.com",
    packages=find_packages(include=["src"]),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
)
