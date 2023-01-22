#!/usr/bin/env bash

show_spinner()
{
  local -r pid="${1}"
  local -r delay='0.1'
  local spinstr='\|/-'
  local temp

  while ps a | awk '{print $1}' | grep -q "${pid}"; do
    temp="${spinstr#?}"
    printf " [%c]  " "${spinstr}"
    spinstr=${temp}${spinstr%"${temp}"}
    sleep "${delay}"
    printf "\b\b\b\b\b\b"
  done
  printf "    \b\b\b\b"
}

("$@") &
show_spinner "sleep 10"

#!/bin/bash
# your real command here, instead of sleep
