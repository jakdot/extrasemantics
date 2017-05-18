from setuptools import setup

VERSION = '0.1.0'

setup(name='extrasemantics',
      version=VERSION,
      description='Less traditional semantic frameworks for nltk and Python',
      url='https://github.com/jakdot/extrasemantics',
      author='jakdot',
      author_email='j.dotlacil@gmail.com',
      packages=['extrasemantics'],
      license='GPL',
      install_requires=['nltk'],
      classifiers=['Programming Language :: Python', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Operating System :: OS Independent', 'Development Status :: 3 - Alpha', 'Topic :: Scientific/Engineering'],
      zip_safe=False)
