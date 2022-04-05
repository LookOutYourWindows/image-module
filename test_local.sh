#!/bin/sh

image=$1

docker run -v $(pwd)/data:/opt/data -v ~/.aws:/root/.aws -p 8080:8080 --rm ${image}