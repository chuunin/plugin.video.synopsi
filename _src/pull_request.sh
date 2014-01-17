
CURRENT_TAG=`git tag --contains $(git rev-parse HEAD)`
VERSION=`echo $CURRENT_TAG | sed 's/....//'`
BRANCH=`git rev-parse --abbrev-ref HEAD`

echo "
[Git Pull] plugin.video.synopsi

* addon - plugin.video.synopsi
* version - $VERSION
* url - git://github.com/Synopsi/plugin.video.synopsi
* revision - $CURRENT_TAG
* branch - $BRANCH
* xbmc version - frodo
"
