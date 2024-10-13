from setuptools import setup, find_packages

setup(
    name='bluebird',  # Package name for PyPI
    version='0.0.1',  # Initial release version
    packages=find_packages(),
    install_requires=[
        'cryptography',  # Main dependency for your crypto utilities
    ],
    description='A Python package for Bluetooth commissioning on Linux with cryptographic utilities baked in',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nichonaugle/bluebird',  # GitHub URL
    author='Nicho Naugle',
    author_email='johndoe123@gmail.com',
    license='MIT',  # Or your preferred license
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',  # Python version requirement
)
