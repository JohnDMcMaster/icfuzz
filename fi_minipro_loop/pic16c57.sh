#!/usr/bin/env bash

dev='PIC16C57'

minipro -p PIC16C57 -y -w 00s.bin

mkdir -p loop

for i in {1..9999}; do
    fn=$(printf loop/out_%04u.bin $i)
    minipro -p $dev -y -r $fn && clear
    echo $fn
    hexdump -C $fn |head -n 30
    echo
    hexdump -C $fn |tail -n 10
    md5sum "$fn"
    sleep 0.5
done

