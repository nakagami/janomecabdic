from setuptools import setup, Extension

try:
    from Cython.Build import cythonize
    ext_modules = cythonize([
        Extension(
            'janomecabdic.dic',
            sources=['janomecabdic/dic.pyx'],
            language='c++',
        ),
    ])
except ImportError:
    ext_modules = None


classifiers = [
    'Development Status :: 4 - Beta',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
]

setup(
    name="janomecabdic",
    version="0.1.0",
    url='https://github.com/nakagami/janomecabdic/',
    classifiers=classifiers,
    license="LGPL2,BSD",
    keywords=['janome', 'MeCab'],
    author='Hajime Nakagami',
    author_email='nakagami@gmail.com',
    description='MeCab dictionary access library for janome',
    long_description=open('README.rst').read(),
    test_suite="tests",
    ext_modules=ext_modules,
)
