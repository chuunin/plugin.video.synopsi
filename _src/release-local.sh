PROJECT_FOLDER=$1

: ${PROJECT_FOLDER:="XBMC"}

rm ${PROJECT_FOLDER}-local.zip
zip -x ${PROJECT_FOLDER}/_src/\* ${PROJECT_FOLDER}/tests/\* \*.pyc -Z store -r ${PROJECT_FOLDER}-local.zip ${PROJECT_FOLDER}/*
RANDSTR=`tr -dc "0-9" < /dev/urandom | head -c 3`

NEWNAME="${PROJECT_FOLDER}-local-$RANDSTR.zip"

echo $NEWNAME
cp ${PROJECT_FOLDER}-local.zip $NEWNAME


