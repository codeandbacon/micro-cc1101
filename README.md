## micro-cc1101
learning how the CC1101 works using micropython

## current hardware
|hardware   |   status  |
|:-         |:-:        |
|esp8266    |working*   |
|esp32      |working    |
|SAMD51     |WIP        |
|STM32      |need hw    |
\* memory issues, need to move to frozen module

#### notes

|<-preamble->|<-sync-->|<-len->|<-addr->|<-data->|<-crc->|

|<--8 * n--->|<-16/32->|<--8-->|<--8--->|<-8*n-->|<-16-->|

#### other rf chips to eventually support

|chip      |ask|ook|2fsk|2gfsk|4fsk|msk|gmsk|psk|lora|note|
|:--       |:-:|:-:|:-: |:-:  |:-: |:-:|:-: |:-:|:-: |:-  |
|cc1101    |Y  |Y  |Y   |Y    |Y   |Y  |    |   |    |WIP |
|RFM69W    |   |Y  |Y   |Y    |    |Y  |Y   |   |    |WIP |
|SX1276    |   |Y  |Y   |Y    |    |Y  |Y   |   |Y   |    |
|SPIRIT1   |Y  |Y  |Y   |Y    |    |Y  |Y   |   |    |find dev board|
|nRF905    |   |   |    |Y    |    |   |    |   |    |    |
|Si4432    |   |Y  |Y   |Y    |    |   |    |   |    |find dev board|
|ATA8510   |Y  |   |Y   |     |    |   |    |   |    |find dev board|
|generic   |Y? |Y  |    |     |    |   |    |   |    |actually possible?*|

\* saw resonator exists, should be possible 