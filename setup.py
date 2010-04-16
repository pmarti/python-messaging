from distribute_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="python-messaging",
      version="0.2",
      description='SMS encoder/decoder',
      license='GPL',
      packages=find_packages(),
      install_requires=['nose >= 0.8.3',],
      zip_safe=True,
      test_suite='messaging.test',
      classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Communications :: Telephony',
        ]
)
