dir_out=loop

help()
{
   echo "Read minipro device in a loop"
   echo
   echo "Syntax: $1 [-dh]"
   echo "d     Directory."
   echo "h     Print this help."
   echo
}

while getopts ":hd" option; do
   case $option in
      d)
        shift
        dir_out="$1"
        ;;
      h) # display Help
         help
         exit;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

mkdir -p "$dir_out"

for i in {1..9999}; do
    fn=$(printf "$dir_out/out_%04u.bin" $i)
    minipro -p $dev -y -r $fn && clear
    echo $fn
    hexdump -C $fn |head -n 30
    echo
    hexdump -C $fn |tail -n 10
    echo
    md5sum $fn
    sleep 0.5
done

