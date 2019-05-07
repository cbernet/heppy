import setuptools
import glob

scripts = glob.glob('bin/*.py')
scripts.remove('bin/__init__.py')
scripts.append('bin/heppy')
print scripts

long_description = """
Heppy is an event processing framework for analyses in High Energy physics. It processes collision
data event by event, creates high-level physics objects and filters, and provides interfaces that
make it possible to write complete physics analyses with ease. While highly customizable through
user-defines analyzers, it includes out-of-the-box functionality, including tools for batch job
submission for certain experiments (currently CMS and FCC).
"""
    
setuptools.setup(
    name='heppyfwk',
    version='3.0.1',
    author='Colin Bernet',
    author_email='colin.bernet@gmail.com',
    description='An event processing framework for High Energy Physics.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cbernet/heppy',
    python_requires='<3.0',
    # Choose your license
    # license='License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='particle physics root',
    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=setuptools.find_packages('.'),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'numpy',
        'scipy',
        'dill',
        'gitpython',
        'pyyaml',
        'ipython'
        ],
    scripts = scripts
)

