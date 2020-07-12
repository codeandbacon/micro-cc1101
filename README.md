## micro-cc1101
learning how the CC1101 works using micropython

## current hardware
esp8266, esp32, more to be added in the future

#### notes

|<-preamble->|<-sync-->|<-len->|<-addr->|<-data->|<-crc->|

|<--8 * n--->|<-16/32->|<--8-->|<--8--->|<-8*n-->|<-16-->|

#### other rf chips to eventually support

|chip      |ask|ook|2fsk|2gfsk|4fsk|msk|gmsk|psk|lora|note|
|:--       |:-:|:-:|:-: |:-:  |:-: |:-:|:-: |:-:|:-: |:-  |
|cc1101    |Y  |Y  |Y   |Y    |Y   |Y  |    |   |    |reference chip|
|RFM69W    |   |   |Y   |Y    |    |Y  |Y   |   |    |    |
|SX1276    |   |Y  |Y   |Y    |    |Y  |Y   |   |Y   |    |
|SPIRIT1   |Y  |Y  |Y   |Y    |    |   |    |   |    |find dev board|
|nRF905    |   |   |    |Y    |    |   |    |   |    |    |
|ATA8510   |Y  |   |Y   |     |    |   |    |   |    |find dev board|
|generic   |Y? |Y  |    |     |    |   |    |   |    |actually possible?*|

\* saw resonator exists, should be possible 