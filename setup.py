import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "numpy",
    "emcee",
    "astropy"
]

setuptools.setup(
    name="emcmass", # Replace with your own username
    version="0.0.1",
    author="Joris Vos",
    author_email="joris.vos@uv.cl",
    description="MC approach to determine stellar masses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vosjo/emcmass",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    test_suite='pytest.collector',
    tests_require=['pytest'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Astronomy",
    ],
    python_requires='>=2.7',
)