# WC3Inside

## Content
`wc3inside/spider` - collection of web spider that collect information about played games.

`wc3inside/web` - webui to display collected data.

`dump` - dataset for MongoDB.

## Install

```
python3 setup.py sdist bdist_wheel && pip install dist/wc3inside-0.0.1-py3-none-any.whl
```

## Usage

Parse game on Azeroth (USEast), starting from game 23191968 and below.
```
wc3inside-parser --gateway Azeroth --debug --init-id 23191968 --old
```
