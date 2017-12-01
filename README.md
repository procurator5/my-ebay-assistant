# my-ebay-assistant

## Install

This software uses python3. I also use framework Django and database PostreSQL.
You need install some packages:

* python 3.5+
* PostgreSQL 9.1+
* django 1.11+
* mttp (Show ebay-categories as tree)
* django-cron (autoload items from ebay)
* django-admin-tools (extra-options for django-admin)
* djorm-ext-pgfulltext (fulltex-search)

### Database settings

You must ensure you have installed the extension unaccent:

```
CREATE EXTENSION unaccent;
ALTER FUNCTION unaccent(text) IMMUTABLE;
```

## Configure

My-ebay-assistant uses eBay API. You must register application on the ebay.com as developer. You can do it here [a link](https://go.developer.ebay.com/).
Configure project after registration from admin dashboard. 

![confugure image](https://github.com/procurator5/my-ebay-assistant/raw/master/docs/settings.png)

You must edit filelds:
* DevID
* AppID
* CertID 