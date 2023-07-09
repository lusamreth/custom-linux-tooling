#!/bin/bash
# All the GLOBAL program variables
#
ITF="wlan0"
DEBUG=0
IW_ENABLE=0
SCANNER_MODE=0
SCANNER_LOCK_FILE=""
IS_CONNECTED=0
# key path is for caching 

key_path="$HOME/wifi_keys"
pkg_dir="$HOME/linux-tools/wifi_tools"
Args=$@
counter=0
auto_connect=false

# wifi resolver options 
# abort on nonzero exitstatus
set -o errexit
# abort on unbound variable
# set -o nounset
# don't hide errors within pipes
set -o pipefail


key_path="$HOME/wifi_keys"
wks_path=($(find $key_path))
spaceToken="??"
# reg_pattern="s/\n/$splitToken/g"
wks_split=($(find $key_path | sed "s/ /$spaceToken/g"))


wifi_key_read(){
    command=$1
    for wk in "${wks_split[@]:1}";do 
        decoded=$(echo $wk | sed "s/$spaceToken/ /g" )
        $command "$decoded"
    done
    unset IFS
}


# OPERATION 
if [ -z "$(pgrep dhcpcd)" ]
then 
    echo 'starting dhcpcd service!'
    doas dhcpcd -b 
fi

dbg_info() { 
    [[ $DEBUG > 0 ]] && echo "[[debug]] $1" || ([[ $2 ]] && echo "$2" || :)
}

ask_loop() {
    read -p "wifi Key path is empty! Would you mind setting a new one?[y/n]" answ 
    echo $answ
    if [[ $answ == "y" || $answ == "Y" ]]; then
        echo "creating dir"
        mkdir $key_path
    else 
        echo "The answer is only yes or no !"
        ask_loop
    fi
}


wpa_ssid_reader() {
    echo $(cat "$1" | grep -i ssid | awk -F "=" '{ print $2}' | tr -d "\"")
}


overlap=()

declare -A hashset 
declare -A wk_cached 

wks_path=$(find $key_path)
ordered_keys=()

# https://stackoverflow.com/questions/9612090/how-to-loop-through-file-names-returned-by-find
gum_box(){
    gum style \
        --foreground 212 --border-foreground 212 --border double \
        --align center --width 50 --margin "1 2" --padding "2 4" \
        $1
}


SSID_CHOICE_ID=""
SCANNED_BUFFER=""

buffer_filtering() {
    [[ $SCANNED_BUFFER == "" ]] && echo "EMPTY SSIDS BUFFER !!"
    SSID_CHOICE_ID="$(echo -e "$SCANNED_BUFFER"  \
        | gum filter --indicator="==>" \
        | cut -d'.' -f1 )"
}

# Inserting wifi_keys into wk_cached registry !
ssid_scanner(){

    leftover_cache=()
    i=0

    source "$pkg_dir/banner.sh"
    dbg_info "Inserting wifi_keys into wk_cached registry !" 
    text_buffer=""
    
    print_buffer() { 
        SCANNED_BUFFER="$text_buffer"
        IFS=$":"
        # print_eol_box $text_buffer
    }

    if [[ $IW_ENABLE == 0 ]];then 
        append_to_cache() {
            wk=$1
            SSID="$(wpa_ssid_reader "$wk")"
            dbg_info "EACH KEY -> $SSID"
            if [[ $SSID == "" ]]; then 
                doas rm "$wk"
                continue
            fi

            wk_cached["$SSID-cached"]="$wk"
            ordered_keys+=("$SSID")
            text_buffer+="$counter.$SSID [cached]\n"
            ((counter+=1))
        }
        wifi_key_read append_to_cache
        print_buffer

        return
    fi
#   leftover_cache+=$SSID
    computed=0

    # echo "TUTUTUTUT ${wk_cached["BinChilling5-cached"]}"
    load_cache() {
        wk=$1
        SSID="$(wpa_ssid_reader "$wk")"
        if [[ $SSID == "" ]];then 
            doas rm $wk
        else 
            # this is because some file name can't be index
            wk_cached["$SSID-cached"]="$wk"
        fi
    }

    wifi_key_read load_cache
    
    for iw in "${!iw_res[@]}";do 
        cached=${wk_cached["$iw-cached"]}
        if [[ $cached != "" ]]; then
            text_buffer+="$counter.$iw [iw-scan][cache]\n"
            hashset[$iw]=1
            overlap+=($counter)
            ordered_keys+=("$iw")
            ((counter+=1))
        else 
            text_buffer+="$counter.$iw [iw-scan]\n"
            ordered_keys+=("$iw")
            ((counter+=1))
        fi
    done

    for raw_cache in "${!wk_cached[@]}"; do 
        cache=$(echo "$raw_cache" | sed "s/-cached//g")
        if [[ ${hashset[$cache]} != 1 ]]; then 
            text_buffer+="$counter.$cache [cached]\n"
            ordered_keys+=("$cache")
            ((counter+=1))
        fi

    done
    print_buffer
}


wpa_connect() {
    dbg_info "mock interface!"
    dbg_info "Successfully initialized wpa_supplicant"
    # dont run actual wpa if debug mode is enable
    IS_CONNECTED=1
    if [ $DEBUG == 0 ]; then 
        doas pkill wpa_supplicant 
        sleep 1
        # if [ ! -z $SCANNER_LOCK_FILE ]; then 
        #     echo "SCANN"
        #     echo "1" >> $SCANNER_LOCK_FILE
        # fi
        gum spin --spinner globe --show-output --title "connecting" -- doas wpa_supplicant -i $ITF -B -c $1
    fi
}

# polish it up
wifi_scanner(){

    if ! [ -d "$key_path" ]; then
        ask_loop
    fi
    if [ $IW_ENABLE == 1 ]; then
        source "$pkg_dir/wifi_signal.sh"
        run_signal_sorting
        # gum spin --spinner dot --title "Buying Bubble Gum..." "iw dev wlan0 scan"
    fi


    combined=( ${!iw_res[@]} "${!wk_cached[@]}" )
    comb_len=${#combined[@]}

    ssid_scanner

    if [ $comb_len > 0 ];then 
    
        prompt="Select your SSID [0-$((counter-1))]: "
        len=(${#overlap[@]})
        echo "[observe] overlap -> [${overlap[@]}|[$len]]"

        if [ $auto_connect == true ]; then 
            keys=(${!hashset[@]})
            if [ $len == 1 ] ; then 
                echo "[auto-on] connecting to ${keys[0]} ${wk_cached["${keys[0]}-cached"]}"
                wpa_connect "${wk_cached["${keys[0]}-cached"]}"

            elif [[ $len > 1 ]] ;then 
                # this is where we perform signal strength comparasion
                # echo "[Debug] ${overlap[@]} ${!hashset[@]}"
                highest=false
                ptr=false
                for overlap_ssid in "${!hashset[@]}"; do 
                    # echo "THIS IS OVELP ${sorted_signals["$overlap_ssid"]} $overlap_ssid ${!sorted_signals[@]}"
                    pos=$(echo  "${sorted_signals["$overlap_ssid"]} * -1" | bc)
                    if [[  $pos < $highest ]] || [[ $highest == false ]]; then
                        highest=${sorted_signals["$overlap_ssid"]}
                        ptr=$overlap_ssid
                    fi
                done

                echo "[auto-on] connecting to the highest signal strength $ptr:$highest"
                wpa_connect "${wk_cached["$ptr-cached"]}"
            else
                echo "NO overlapp found "
            fi

        else 
        
            buffer_filtering 
            selected=${ordered_keys[$SSID_CHOICE_ID]}
            cached_ssid=${wk_cached["$selected-cached"]} 

            echo "[manual] selected $selected"
            status="$( [[ "$cached_ssid" != "" ]] \
                && echo $cached_ssid \
                || echo "[[ wlan0-scan ]]")"
            echo "[manual] connecting to $selected -> $status"

            if [[ "$cached_ssid" != "" ]]; then 
                wpa_connect "${wk_cached["$selected-cached"]}"
            else 
                echo -e "*please insert your passwrd ->\n"
                pass="$(gum input --password --prompt "wifi passwd : ")"
                target="$key_path/$(echo $selected | tr "[:upper:]" "[:lower:]" | sed "s/ /_/g" )"
                set +o history

                psk=$(doas wpa_passphrase "$selected" "$pass" | doas tee "/etc/wpa_supplicant.conf" )
                echo "$psk" | tee "$target"
                wpa_connect "/etc/wpa_supplicant.conf"
                set -o history

            fi
        
        fi

    else 
        echo "No ssid is found!"
        exit 1 
    fi
    
}


ONLINE_STATUS=$(ping -q -c1 google.com &>/dev/null && echo online || echo offline)
arg_counter=0

INDEX=0
for a in ${Args[@]}; do 
    case "$a" in
        # automatically 
        "-i" )
        echo "IW MODE ENABLE !"
        IW_ENABLE=1;;
        "-c" )
        IW_ENABLE=0;;
        "-a" ) 
        auto_connect=true;;
        "-d" )
        echo "DEBUG MODE ENABLE !"
        DEBUG=1;;
        "-s" )
        echo "SCANNER MODE ENABLE !"
        let nxt_index=${INDEX}+1
        conv=(${Args[@]})
        nextItem=${conv[$nxt_index]}
        if [[ -z $nextItem ]];then 
            echo "scanner mode must provide lock file"
            exit 1
        fi
        SCANNER_LOCK_FILE="$nextItem"
        SCANNER_MODE=1;;
        # *)
        # echo "Unknown argument !"
        # exit 1;;

    esac
    let INDEX=${INDEX}+1
done

echo "WII $auto_connect"
if [[ $auto_connect == true ]] && [[ $IW_ENABLE == 0 ]] ;then
    echo "iw tools must be enable to work!" 
    echo "enable via option -i"
    exit 1
fi

if [[ $SCANNER_MODE == 1 ]] && [[ $auto_connect == false ]] ;then
    echo "auto connect feature must be enable to work!" 
    echo "enable via option -a"
    exit 1
fi


if [[ $SCANNER_MODE == 1 ]];then 
    LOCK_STATE="$(cat $SCANNER_LOCK_FILE)"
    if [[  "$ONLINE_STATUS" == "online"  ]];then 
        echo "cancel scanning because wifi is already online!"
    fi
    while [[ $IS_CONNECTED != 1 ]] && [[ "$ONLINE_STATUS" == "offline" ]]; do
        echo $IS_CONNECTED
        echo $SCANNER_LOCK_FILE
        echo "connect wifi..." 
        wifi_scanner 
        sleep 2
    done

    echo "wifi found!!" 
else 
    wifi_scanner 
fi
