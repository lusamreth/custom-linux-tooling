OUT="$(mktemp /tmp/output.XXXXXXXXXX)" || { echo "Failed to create temp file"; exit 1; }
status=$(ping -q -c1 google.com &>/dev/null && echo online || echo offline)
bash ~/linux-tools/wifi_tools/connect_wifi.sh -i -a -s $OUT 
