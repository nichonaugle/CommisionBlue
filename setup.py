from setuptools import setup, find_packages

setup(
    name='bluebird',  # Package name for PyPI
    version='0.0.1',  # Initial release version
    packages=find_packages(),
    install_requires=["cryptography (==43.0.1)", "certifi (==2024.8.30)", "cffi (==1.17.1)", "charset-normalizer (==3.4.0)", "dbus-python (==1.3.2)", "idna (==3.10)", "pycairo (==1.27.0)", "pycparser (==2.22)", "pygobject (==3.50.0)", "requests (==2.32.3)", "urllib3 (==2.2.3)"],
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
    python_requires='<4.0,>=3.9',  # Python version requirement
)
