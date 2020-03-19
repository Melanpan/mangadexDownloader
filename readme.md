### Overview

A small program that, when ran as cron, will download the latest chapters from Mangadex and notify you through pushover once they are downloaded. Written in Python3.7 and inspired by frozenpandaman's mangadex-dl.

### Usage
It currently takes no arguments, just simply run it from the command line or a cron.

### Config
Here is an example config file, the syntax is yaml and the config has to be saved as config.yaml
```yaml
downloadpath: "/mnt/manga/"
check_last_items: 1
 
 naming:
  volumes: True

pushover:
  user: <user token>
  token: <application token>
  enabled: True
  
mangas:
   - id: 31004
     name: ijiranaide-nagatoro-san-comic-anthology
     cover: true
     check_last: true
     group:
      - "/a/nonymous"
      
   - id: 16193
     name: charlotte
     cover: true
     check_last: True
     group:
       - "/r/CharlotteAnime"
       - "Kana the Good Librarian"
    
```

Explanation of the settings


| Setting               | Description                              | Required
|-----------------------|------------------------------------------|------------------------------------------|
| downloadpath        | the path to download all the pages to. | Yes
| check_last_items       | How many of the last chapsters to check for availability.      | Yes
| naming:volumes    | Set to true to save chapters in a folder of the volume they belong to. | Yes
| pushover:user             | Your pushover user token. | Yes (when using pushover)
| pushover:token             | Your pushover application token. | Yes (when using pushover)
| pushover:enabled      | Set to true to enable pushover. | Yes
| manga:id    | The id of the manga on Mangadex | Yes
| manga:name | The name of the manga, used as download path | Yes
| manga:cover | Enable this to also download the cover image | No
| manga:check_last | Set to true if you want to only check the x amount of last chapters, set to false if you want to download all available chapters | False
| manga:group | A list of scanlation groups to download | Yes

### Shortcomings
- Currently there is no way to set what language you want, it's hard-coded to be set to English
- You have to tell it what group to download from, otherwise it won't work. In the future I want it to being able to fall back to whatever group once a new chapter is out.
- It doesn't really handle exceptions well yet.
- It doesn't actually have any delay between downloading pages and chapters, now this hasn't given me any problems at all, you have been warned.
- It doesn't work under windows yet