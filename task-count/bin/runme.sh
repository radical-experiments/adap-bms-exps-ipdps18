#!/bin/bash

export RADICAL_PILOT_DBURL="mongodb://entk:entk123@ds121332.mlab.com:21332/ipdps-bms-tc-1"
export RADICAL_ENTK_PROFILE=True
export RADICAL_PILOT_PROFILE=True
export RADICAL_ENTK_VERBOSE=INFO
export RADICAL_PILOT_VERBOSE=DEBUG

stages="16 64 256"
for s in $stages; do
    mkdir stages-$s
    python runme.py $s
    radical-pilot-fetch-profiles rp.session.*
    radical-pilot-fetch-json rp.session.*
    mv re.session* rp.session.* stages-$s/
done
