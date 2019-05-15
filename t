#! /bin/bash

python3 -m pytest . -v -Wignore:"The object should be created from async function":DeprecationWarning:aiohttp.connector -Wignore:"The object should be created from async function":DeprecationWarning:aiohttp.cookiejar -Wignore:"The object should be created from async function":DeprecationWarning:telepot.aio.api

