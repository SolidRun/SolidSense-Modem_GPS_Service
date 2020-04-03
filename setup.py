#-------------------------------------------------------------------------------
# Name:        setup for modem GPS service
# Purpose:
#
# Author:      Laurent Carré
#
# Created:     06/12/2019
# Copyright:   (c) Laurent Carré Sterwen Technologies 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SolidSense-Modem-GPS", # Replace with your own username
    version="1.2.1",
    author="Laurent Carré",
    author_email="laurent.carre@sterwen-technology.eu",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SolidRun/SolidSense-Modem_GPS_Service",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.6',
)
