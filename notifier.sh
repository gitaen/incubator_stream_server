#!/bin/sh

SLACK_URL=fill it in here
TIMELEFT=$(cut -d ' ' -f 14)
if [ $TIMELEFT -le 180 ] && [ $TIMELEFT -gt 120 ]; then
    curl -X POST --data-urlencode 'payload={
        "channel": "#anonymous",
        "text":"<!here> ¡Huevos a puntito de girar! http://pollo-o-matic.us.to/",
        "username": "Pollo-o-Matic",
        "icon_emoji": ":egg:"
    }' \
    	 $SLACK_URL
fi
