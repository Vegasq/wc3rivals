# WC3Inside

## Content
`wc3inside/spider` - collection of web spiders that collect information about played games.

`wc3inside/web` - webui to display collected data.

`dump` - dataset for MongoDB.

## Install

Create `.env` file in root folder with next content:

```
# MongoDB settings:
WC3I_HOSTNAME=mongo_ip
WC3I_USERNAME=mongo_user
WC3I_PASSWORD=mongo_password
```

To generate whl:
```
./build.sh
```

Now build and start containers:

```
docker-compose up --build
```

Dump was taken with:

```
mongodump -d battle --gzip  --host=... -u ... --password="..." --authenticationDatabase=admin
```
