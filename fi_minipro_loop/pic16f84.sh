dev='PIC16F84'

rm -rf loop
mkdir -p loop

for i in {1..9999}; do
    fn=$(printf loop/out_%04u.bin $i)
    minipro -p $dev -y -r $fn -c code && clear
    echo $fn
    hexdump -C $fn |head -n 40
    sleep 0.5
done

