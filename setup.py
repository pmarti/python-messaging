from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name="python-messaging",
      version='0.5.0',
      description='SMS encoder/decoder',
      license='GPL',
      packages=find_packages(),
      install_requires=['nose >= 0.8.3',],
      zip_safe=True,
      test_suite='messaging.test',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Communications :: Telephony',
        ],
      **extra
)
