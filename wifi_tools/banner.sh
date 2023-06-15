
banner() {
    msg="# $* #"
    edge=$(echo "$msg" | sed 's/./#/g')
    echo "$edge"
    echo "$msg"
    echo "$edge"
}

function pretty_print(){
    xargs -d '\n' -I {} echo '{{ Color "99" "0"  "{}" }}' | gum format -t template 
}

function box_out()
{
  local s=("$@") b w
  for l in "${s[@]}"; do
    ((w<${#l})) && { b="$l"; w="${#l}"; }
  done
  tput setaf 3
  pipe="||"
  echo "---${b//?/-}---" | pretty_print
  echo "$pipe ${b//?/ } $pipe" | pretty_print
  for l in "${s[@]}"; do
    printf "$pipe %s%*s%s $pipe\n" "$(tput setaf 4)" "-$w" "$l" "$(tput setaf 3)" \
        | pretty_print
  done
  echo "$pipe ${b//?/ } $pipe" | pretty_print
  echo "---${b//?/-}---" | pretty_print
  tput sgr 0
}

print_eol_box(){
    OIFS="${IFS}"
    IFS=$"\n"
    msg=($1)
    IFS="${OIFS}"
    box_out ${msg[@]} 
}

# epo="xdbruh\ndodo\n"
# print_eol_box $epo

