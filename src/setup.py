from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

version = 1.0

setup(
    name="CharacterCreators",
    version=version,
    python_requires=">=3.7.4",
    packages=find_packages(),
    install_requires=requirements
)
