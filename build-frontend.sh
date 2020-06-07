#!/bin/bash

cd ./frontend/transcriber-front && yarn install && yarn build && cd ../.. ;
cp -r ./frontend/transcriber-front/build ./backend-webrtc ;


