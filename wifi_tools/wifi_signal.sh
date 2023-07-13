#!/bin/bash 
# this script is responsible for searching all the wifi SSID and 
# also sort signal

declare -A iw_res
declare -A signals
declare -A sorted_signals
declare -A reversed_sorted_signals

rws=0
pkg_dir="$HOME/linux-tools/wifi_tools"

extract() {
    rws=$(doas iw dev wlan0 scan | \
        awk -f "$pkg_dir/iw_grab.awk" \
        | tr -d ' ')
}

exec_iw_scan() {
    # iw_res+=$(doas iw dev wlan0 scan | grep -i ssid | awk -F ":" '{ print $2 }' | awk '{ gsub(/ /,""); print }')
    raw_scan=$(gum spin --spinner globe -a right \
        --title "Scanning all the available SSIDs" \
        --show-output \
        doas iw dev wlan0 scan | \
        awk -f "$pkg_dir/iw_grab.awk" | tr -d ' ') 

    parsed_newline=${raw_scan%$'\n'*}
    for iw_pair in $parsed_newline; do 
        ssid=$(echo $iw_pair | awk -F"," '{ print $1 }' \
            | sed "s/-?/ /g" | sed "s/ //" )
        
        signal_str=$(echo $iw_pair | awk -F"," '{ print $2 }' | tr -d "dBm" )
        if [[ $ssid == "" ]];then 
            echo "Found empty name SSID!"
        else 
            iw_res["$ssid"]="$signal_str"
            signals["$signal_str"]="$ssid"
        fi
     
    done
}

# fix signal sorting algorithm
# test in other file plsisss

declare -A testing_signal_dict
test_signal (){
    order=0
    signal_amount=10
    initial_signal=2

    test_ssid="test-prefix"
    for ((order=0; order<=$signal_amount;order++));do 

        noise=$(echo $(( $RANDOM % 113 + 1 )))
        # dBm is generated in a negative number
        testing_signal_dict["$test_ssid-$order"]="-$((noise + initial_signal * order))"

        echo "-$((noise + initial_signal))  ${testing_signal_dict["$test_ssid-$order"]}"
    done

    # echo ${!testing_signal_dict[@]}
    
}

sorting_signal() {
    # reverse signal 
    verbose=false
    if [ "$1" == "-v" ] ; then 
        verbose=true
        echo "verbose mode on !"
    fi
    sorted_keys=($(echo "${!signals[@]}"| tr " " "\n" | sort -n  | tr "\n" " "))
    for sorted_key in "${sorted_keys[@]}";do 
        if [[ $verbose == true ]];then 
            echo "[[verbose]] $sorted_key  , ${signals[$sorted_key]}"
        fi
        # declare -A sorted_signals=(["${signals[$sorted_key]}"]=$sorted_key)
        sorted_signals["${signals[$sorted_key]}"]=$sorted_key
        reversed_sorted_signals["$sorted_key"]=${signals[$sorted_key]}
    done
}

# [ testing code ]
testing_sorting_signal() { 
    test_signal 

    echo ${testing_signal_dict[@]}
    # copy to signal variabel
    for ts in "${!testing_signal_dict[@]}"; do
        # reverse here 
        val=${testing_signal_dict["$ts"]}
        echo "ts $ts"
        signals["$val"]=$ts
    done
}


run_signal_sorting() {
    fallback_opt=$1
  set -Ee
  function _catch {
    case "$fallback_opt" in 
        "restart-always" ) 
          echo "restarting..." 
          exec_iw_scan
          sorting_signal
          ;;
        "crash" )
          echo "closing"
          exit 0
          ;;
        * ) 
            echo "defualt"
          ;;
    esac
    # exit 0  # optional; use if you don't want to propagate (rethrow) error to outer shell
  }
  function _finally {
    echo "scanning done!"
  }
  trap _catch ERR
  trap _finally EXIT
  exec_iw_scan
  sorting_signal
    
}
