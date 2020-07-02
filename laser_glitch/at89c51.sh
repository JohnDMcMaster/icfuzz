dev='AT89C51'

mkdir -p loop

for i in {1..9999}; do
    fn=$(printf loop/out_%04u.bin $i)
    minipro -p $dev -y -r $fn && clear
    echo $fn
    hexdump -C $fn |head -n 40
    sleep 0.5
done

