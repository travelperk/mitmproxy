#!/bin/sh
if [ $# -eq 0 ]
  then
    echo "Please provide the release name example push.sh latest"
    exit 1
fi

VERSION=$1

eval $(aws ecr get-login --no-include-email --region eu-west-1)
docker build -t mitmproxy:$VERSION -f Dockerfile .
docker tag mitmproxy:$VERSION 264159233651.dkr.ecr.eu-west-1.amazonaws.com/mitmproxy:$VERSION
docker push 264159233651.dkr.ecr.eu-west-1.amazonaws.com/mitmproxy:$VERSION
