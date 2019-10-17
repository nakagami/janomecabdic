from setuptools import setup, Extension

classifiers = [
    'Development Status :: 3 - Alpha',
    'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)'
    'License :: OSI Approved :: BSD License'
    'Operating System :: POSIX :: Linux'
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
]

setup(
    name="janomecabdic",
    version="%d.%d.%d" % __import__('janomecabdic').VERSION,
    url='https://github.com/nakagami/janomecabdic/',
    classifiers=classifiers,
    license="LGPL2,BSD",
    keywords=['janome', 'MeCab'],
    author='Hajime Nakagami',
    author_email='nakagami@gmail.com',
    description='MeCab dictionary access library for janome',
    long_description=open('README.rst').read(),
    test_suite="tests",
    setup_requires=["cython"],
    ext_modules=[
        Extension(
            'janomecabdic.dic',
            sources=['janomecabdic/dic.pyx'],
            language='c++',
        ),
    ],
)
