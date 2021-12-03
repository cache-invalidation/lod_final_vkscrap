# lod_final_vkscrap

This is a convenience layer for data collection on the VK social network we've implemented as part of our solution for Leaders of Digital Hackathon.

## Installation
First of all, you should install the requirements:

```
pip install -r requirements.txt
```
After that, you will need to create file `credentials.py` in the library's folder with the following content:

```
VK_LOGIN = <VK_LOGIN_FOR_SCRAPPER_ACCOUNT>
VK_PASSWORD = <VK_PASSWORD_FOR_SCRAPPER_ACCOUNT>
VK_TOKEN = <VK_TOKEN_FOR_SCRAPPER_ACCOUNT>

ANTICAPTCHA_KEY = None
```

Note that anticaptcha support has not been implemented yet, so you don't need to provide key. We strongly suggest using separate account for scraping, as there is a chance that it'll eventually get banned.
