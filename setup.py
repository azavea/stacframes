from setuptools import find_packages, setup

setup(
    name="stacframes",
    version="0.1.0",
    description="Python library providing a compatibility layer between pystac and geopandas GeoDataFrames",
    author="Azavea",
    author_email="info@azavea.com",
    url="https://github.com/azavea/stacframes",
    license="Apache Software License 2.0",
    packages=find_packages(),
    install_requires=["pystac>=0.5.0", "geopandas>=0.7.0"],
    keywords=["pystac", "pandas", "DataFrame"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
