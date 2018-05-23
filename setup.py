import setuptools


setuptools.setup(
    name="wc3inside",
    version="0.0.1",
    author="Mykola Yakovliev",
    author_email="vegasq@gmail.com",
    description="wc3inside",
    url="https://github.com/vegasq/wc3inside",
    packages=setuptools.find_packages(),
    py_modules=["wc3inside/web/", "wc3inside/utils/", "wc3inside/spider"],
    include_package_data=True,
    data_files=[("wc3inside", ["wc3inside/web/templates/app.js",
                               "wc3inside/web/templates/solo_stats.html"])],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'wc3inside-parser=wc3inside.spider.gamesparser:main',
            'wc3inside-parser-ladder=wc3inside.spider.ladderparser:main',
            'wc3inside-server=wc3inside.web.serv:main',
        ],
    }
)
