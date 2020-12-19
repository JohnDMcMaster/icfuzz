dev='AT89C51'
fn=~/doc/ext/icfuzz/patgen/mcs51/at89c51_c16.bin

mkdir -p loop
rm -f loop/*

# wanted to write + lock but its not easy to do from CLI
# minipro -p $dev -y -r loop/readback.bin

for i in {1..9999}; do
    fn=$(printf loop/out_%04u.bin $i)
    minipro -p $dev -y -r $fn && clear
    echo $fn
    hexdump -C $fn |head -n 40
    sleep 0.5
done

