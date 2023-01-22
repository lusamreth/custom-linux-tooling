BEGIN{ FS=":" } 

/signal:/{ 
    gsub("/ /","",$2)
    signal[e++]=$2 
}
/SSID:/{ 
    gsub(" ","-?")
    if (length($2) == 1){
        ssid[d++]="hidden"
    }else{
        ssid[d++]=$2
    }
}
END{
    for (a in ssid){ 
      print (ssid[a],",",signal[a])
    }
}

