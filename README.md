# pico_display
A small display to show information for PC connect with USB. Using Raspberry Pi pico and micro python
這是用於一個自製的小型顯示設備，它的最終目標是能配合改過的 lcdproc 來顯示 Linux 系統的資訊。
然而在沒連接主機程式的時候，它亦可當獨立的時鐘以及提供一些額外功能。然而，當前後者竟然變成了主要改進點了，因為實在沒時間搞懂 lcdproc. 這個日後再想辦法。

使用硬體：
1. Raspberry Pi Pico 機板 : https://www.raspberrypi.com/products/raspberry-pi-pico/ 我的是最陽春版本。
2. Waveshare Pico-LCD 1.14 : https://www.amazon.com/TOP1-Raspberry-1-14inch-Resolution-Communication/dp/B08VSJVF1Y Waveshare 官網的產品已經不太一樣了，我的是舊版。
3. 按鈕開關一個，當 Reset button
4. DS18B20 溫度感應器: 因為實際測試， Raspberry Pi Pico 內建的溫度測量數值誤差比較大，所以後來改用外部溫度測量。
5. 光敏電阻：提供將來自動調整亮度功能
6. DS3231 RTC 模組：使用這個保持系統時間正確。

配線：
日後補上

使用軟體：
st7789-mpy: https://github.com/russhughes/st7789_mpy 為了便於使用 LCD, 我使用這個韌體當基礎
ds3231-port: https://github.com/peterhinch/micropython-samples/blob/master/DS3231/ds3231_port.py
ds18x20: https://github.com/robert-hh/Onewire_DS18X20

目錄結構:
pico_lcd: 放到 Raspberry Pi Pico 上的檔案


