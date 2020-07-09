## micro-cc1101
learning how the CC1101 works using micropython

## current hardware
esp8266, esp32, more to be added in the future

#### notes

|<-preamble->|<-sync-->|<-len->|<-addr->|<-data->|<-crc->|

|<--8 * n--->|<-16/32->|<--8-->|<--8--->|<-8*n-->|<-16-->|

|chip|2fsk|gfsk|ask|psk|note|
|:--|:--:|:--:|:--:|--|--|
|cc1101|Y|Y|Y|||
|RFM69HCW|Y|Y|Y||
|SX1276|Y|Y|Y|||
|SPIRIT1|Y|Y|Y|?|find more info|
|nRF905|?|Y|N|N|
|generic?|N|N|Y|N|915Mhz exists?*|

\* saw resonator exists, should be possible 