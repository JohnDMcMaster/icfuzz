while true; do
    printf '.'
    rm -f code.bin
    minipro -p PIC16F84 -c code -r code.bin >read.txt
    if [ $(md5sum read.txt|cut -d' '  -f 1) = 882c83ba176f526a094f0cc0fd6d990b ] ; then
        echo
        cat read.txt
    fi
    if [ $(md5sum code.bin|cut -d' '  -f 1) = d41d8cd98f00b204e9800998ecf8427e ] ; then
        echo
        hexdump -C code.bin |head
    fi
    sleep 0.1
done

