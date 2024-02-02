#!/bin/sh
npx rollup index.js -p @rollup/plugin-node-resolve -f iife -o index.bundle.js \
    && mv index.bundle.js ../guiren/public/assets/