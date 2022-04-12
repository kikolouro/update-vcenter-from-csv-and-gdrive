#!/bin/bash
source .env
 
docker build -t updatevcenter:$APPVERSION .
docker run --restart unless-stopped updatevcenter:$APPVERSION 
