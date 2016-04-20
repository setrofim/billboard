import os
import sys
import warnings
from setuptools import setup


# happends if falling back to distutils
warnings.filterwarnings('ignore', "Unknown distribution option: 'install_requires'")
warnings.filterwarnings('ignore', "Unknown distribution option: 'extras_require'")

try:
    os.remove('MANIFEST')
except OSError:
    pass

packages = []
data_files = {}
source_dir = os.path.dirname(__file__)
billboard_dir = os.path.join(source_dir, 'billboard')
for root, dirs, files in os.walk(billboard_dir):
    rel_dir = os.path.relpath(root, source_dir)
    data = []
    if '__init__.py' in files:
        for f in files:
            if os.path.splitext(f)[1] not in ['.py', '.pyc', '.pyo']:
                data.append(f)
        package_name = rel_dir.replace(os.sep, '.')
        package_dir = root
        packages.append(package_name)
        data_files[package_name] = data
    else:
        # use previous package name
        filepaths = [os.path.join(root, f) for f in files]
        data_files[package_name].extend([os.path.relpath(f, package_dir) for f in filepaths])

scripts = [os.path.join('scripts', s) for s in os.listdir('scripts')]

params = dict(
    name='billboard',
    description='Periodically changing text and backgrounds',
    version='0.0.1',
    packages=packages,
    package_data=data_files,
    scripts=scripts,
    url='N/A',
    license='3-clause BSD',
    maintainer='setrofim',
    maintainer_email='setrofim@gmail.com',
    install_requires=[
        #'PyQt4',
        'requests',
        'praw',
    ],
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.4',
    ],
)

setup(**params)
