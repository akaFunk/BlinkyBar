# Alternative: https://gist.github.com/mcous/5920089

# Fuses with external 8 MHz crystal
LFU = 0xFF
HFU = 0xDA
EFU = 0xFD

# Programmer options for Atmel ICE in ISP mode
PROGRAMMER=atmelice_isp
PORT=usb

BIN=module
OBJS=main.o uart.o fifo.o ws2812b.o flash.o flash_sm.o
AVRDUDE=avrdude
CC=avr-gcc
OBJCOPY=avr-objcopy
DEVICE=ATMEGA328P
DEVICE_SMALL=atmega328p
CFLAGS=-O2 -DF_CPU=8000000UL -mmcu=${DEVICE_SMALL} -Wall

${BIN}.hex: ${BIN}.elf
	${OBJCOPY} -O ihex -R .eeprom $< $@

${BIN}.elf: ${OBJS}
	${CC} ${CFLAGS} -o $@ $^
	avr-size -C --mcu=${DEVICE_SMALL} ${BIN}.elf

size:
	avr-size -C --mcu=${DEVICE_SMALL} ${BIN}.elf

%.o: %.c
	${CC} ${CFLAGS} -c -o $@ $<

fuses:
	$(AVRDUDE) -F -V -c $(PROGRAMMER) -p $(DEVICE) -B 10 -P $(PORT) -U lfuse:w:$(LFU):m -U hfuse:w:$(HFU):m -U efuse:w:$(EFU):m

flash: ${BIN}.hex
	$(AVRDUDE) -F -V -c $(PROGRAMMER) -p $(DEVICE) -B 1 -P $(PORT) -U flash:w:$<

clean:
	rm -f ${BIN}.elf ${BIN}.hex ${OBJS}

# The assembler files are only used for debugging
%.s: %.c
	${CC} ${CFLAGS} -S -o $@ $<
