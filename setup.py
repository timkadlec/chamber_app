#  Copyright (c) 2024. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from setuptools import setup, find_packages

setup(
    name="chamber_app",  # Your project name
    version="0.1",  # Your project version
    packages=find_packages(),  # Automatically find packages in the project
    include_package_data=True,  # Include files from MANIFEST.in
    install_requires=[         # Add required packages from requirements.txt
        line.strip() for line in open("requirements.txt").readlines() if not line.startswith('#')
    ],
    entry_points={
        'console_scripts': [
            # Add console scripts here if your project has CLI commands
        ],
    },
)