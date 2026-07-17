from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='SteamTableGUI',
    version='0.0',
    include_package_data=True,
    python_requires='>=3.4',
    packages=find_packages(),
    setup_requires=['setuptools-git-versioning'],
    install_requires=requirements,
    author='Ryan Hoover',
    author_email='rhoover@pointpark.edu',
    description="A GUI for Steam Table lookups",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown"
)
