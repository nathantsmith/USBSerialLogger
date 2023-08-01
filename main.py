import machine
import os
import ujson
import utime

# Set up the USB serial connection
uart = machine.UART(1, baudrate=9600)

# SD card SPI connection setup
spi_sck = machine.Pin(10, machine.Pin.OUT)
spi_mosi = machine.Pin(11, machine.Pin.OUT)
spi_miso = machine.Pin(12, machine.Pin.OUT)
spi_cs = machine.Pin(13, machine.Pin.OUT)

spi = machine.SPI(0, baudrate=10000000, sck=spi_sck, mosi=spi_mosi, miso=spi_miso)

sd = machine.SDCard(slot=0, cs=spi_cs)
os.mount(sd, '/sd')

buffer = ""
start_time = utime.ticks_ms()
file_index = 0

while True:
    # Check for incoming data
    if uart.any():
        data = uart.read().decode()  # read and decode
        buffer += data

        # Check for valid JSON in the buffer, by checking for closing bracket
        if "}" in buffer:
            json_end = buffer.index("}")
            json_raw = buffer[:json_end+1]
            buffer = buffer[json_end+1:]  # remove the processed json data from buffer

            try:
                json_data = ujson.loads(json_raw)  # Assuming data is JSON
                # append to the current file
                with open('/sd/data_{}.txt'.format(file_index), 'a') as f:
                    f.write(ujson.dumps(json_data))
            except ValueError:
                pass  # JSON was malformed, you may want to log this

    # Check if 6 hours have passed
    if utime.ticks_diff(utime.ticks_ms(), start_time) > 6 * 60 * 60 * 1000:
        file_index += 1
        start_time = utime.ticks_ms()
