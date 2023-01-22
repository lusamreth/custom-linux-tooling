
key_path="$HOME/wifi_keys"
wks_path=($(find $key_path))

# splitToken="xbbb<[]"
spaceToken="??"

reg_pattern="s/\n/$splitToken/g"
# wks_split=$(find $key_path | sed -e ':a' -e 'N' -e '$!ba' -e $reg_pattern | sed "s/ /$spaceToken/g")
wks_split=$(find $key_path | sed "s/ /$spaceToken/g")

# IFS=$"$splitToken"

wifi_key_read(){
    command=$1
    for wk in $wks_split;do 
        decoded=$(echo $wk | sed "s/$spaceToken/ /g" )
        $command "$decoded"
    done
}

pru(){
    echo "hshs $1"
}
reada pru
# echo $wks_path
# while IFS= read -r line; do # Whitespace-safe EXCEPT newlines
#     echo "reader $line"
# done < "$(find $key_path)"
