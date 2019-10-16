from setuptools import setup, Extension


setup(
    name="janomecabdic",
    test_suite="tests",
    setup_requires=["cython"],
    ext_modules=[
        Extension(
            'janomecabdic.dic',
            sources=['janomecabdic/dic.pyx'],
            language='c++',
        ),
    ]
)


