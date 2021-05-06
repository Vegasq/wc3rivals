import setuptools


setuptools.setup(
    name="wc3rivals",
    version="0.0.1",
    author="Mykola Yakovliev",
    author_email="vegasq@gmail.com",
    description="wc3rivals",
    url="https://gitlab.com/vegasq/wc3rivals",
    packages=setuptools.find_packages(),
    py_modules=["wc3rivals/utils/"],
    include_package_data=True,
    data_files=[],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'wc3rivals-parser=wc3rivals.spider:main',
            'wc3rivals-db-manage=wc3rivals.utils.index_creation:up'
        ],
    },
    install_requires=[
        "beautifulsoup4==4.6.0",
        "certifi==2018.4.16",
        "chardet==3.0.4",
        "idna==2.6",
        "pymongo==3.6.1",
        "requests==2.20.0",
        "urllib3==1.24.2",
        "flask==1.0.2",
        "flask-cors==3.0.9"
    ]
)
