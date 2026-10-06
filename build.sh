#!/bin/bash
set -e

rm -rf public
mkdir -p public/_astro

cp -r pages/. public/
cp -r assets/. public/

cp assets/css/about.Cl92HC4C.css public/_astro/about.Cl92HC4C.css
cp build/fix.js public/_astro/fix.js

python3 build/inject.py
