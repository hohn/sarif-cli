from setuptools import setup
import glob

setup(name='sarif_cli',
      version='0.1',
      description='Collection of command line tools for sarif files',
      url='https://github.com/hohn/sarif-cli',
      author='Michael Hohn',
      author_email='hohn@github.com',
      license='MIT',
      packages=['sarif_cli'],
      install_requires=[],
      include_package_data=True,
      scripts=glob.glob("bin/sarif-*"),
      zip_safe=False,
      python_requires='>=3.7'
      )
