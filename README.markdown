# SynopsiTV XBMC plugin

## plugin.video.synopsi

This is SynopsiTV App that provides reccomendations. IN ALPHA PHASE!!

## service.synopsi

This is deamon that starts on startup or login and runs in the background.

It sends whole movie library on startup and waits for user's interaction with movies. 

### Sends

User's interaction Json:
```
{
        "data": {
            "TotalTime": "5377.0",
            "File2": "",
            "Title": "A Very Harold & Kumar Christmas",
            "Status": "paused",
            "IMDB": "tt1268799",
            "File": "",
            "Time": "4229.011200867244",
            "Path": ""
        }
    }
```

User's movie database: !!May change
```
{
    "token": 12345,
    "data": [
        {
            "IMDB ID": "tt1268799",
            "Path": "C:\\\\dmd-vhakc.avi",
            "Local Movie Title": "A Very Harold & Kumar Christmas",
            "Original Movie Title": "A Very Harold & Kumar Christmas"
        },
        {
            "IMDB ID": "tt0110116",
            "Path": "",
            "Local Movie Title": "Immortal Beloved",
            "Original Movie Title": "Immortal Beloved"
        }
    ]
}
```


### Installation

#### For users
* Download zip and install as zip
* Add public repository #TODO

#### For developers
##### Windows
Download zipball. Extract content to C:\Users\Username\AppData\Roaming\XBMC\addons .

##### UNIX
TODO
