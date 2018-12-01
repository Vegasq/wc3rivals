import setuptools


setuptools.setup(
    name="wc3inside",
    version="0.0.1",
    author="Mykola Yakovliev",
    author_email="vegasq@gmail.com",
    description="wc3inside",
    url="https://github.com/vegasq/wc3inside",
    packages=setuptools.find_packages(),
    py_modules=["wc3inside/web/", "wc3inside/utils/", "wc3inside/spider/"],
    include_package_data=True,
    data_files=[("wc3inside", ["wc3inside/templates/app.js",
                               "wc3inside/templates/solo_stats.html"])],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'wc3inside-parser=wc3inside.spider.gamesparser:main',
            'wc3inside-parser-ladder=wc3inside.spider.ladderparser:main',
            'wc3inside-server=wc3inside.web.serv:main',
            'wc3inside-stats=wc3inside.utils.stats_calc:main',
        ],
    },
    install_requires=[
        "beautifulsoup4==4.6.0",
        "certifi==2018.4.16",
        "chardet==3.0.4",
        "idna==2.6",
        "pymongo==3.6.1",
        "requests==2.18.4",
        "urllib3==1.22",
        "web.py==0.40.dev1",
        "jinja2==2.10"
    ]
)
