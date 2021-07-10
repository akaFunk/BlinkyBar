# Alternative: https://gist.github.com/mcous/5920089

# Fuses with external 8 MHz crystal
#LFU = 0xFF
#HFU = 0xDA
#EFU = 0xFD

# Fuses with external 8 MHz clock (NOT CRYSTAL!)
LFU = 0xE0
HFU = 0xDA
EFU = 0xFD

# Programmer options for Atmel ICE in ISP mode
PROGRAMMER=atmelice_isp
PORT=usb

BIN=blinkybar_module
OBJS=main.o uart.o fifo.o ws2812b.o
AVRDUDE=avrdude
CC=avr-gcc
OBJCOPY=avr-objcopy
DEVICE=ATMEGA328P
CFLAGS=-Os -DF_CPU=8000000UL -mmcu=atmega328p

${BIN}.hex: ${BIN}.elf
	${OBJCOPY} -O ihex -R .eeprom $< $@

${BIN}.elf: ${OBJS}
	${CC} ${CFLAGS} -o $@ $^

%.o: %.c
	${CC} ${CFLAGS} -c -o $@ $<

fuses:
	$(AVRDUDE) -F -V -c $(PROGRAMMER) -p $(DEVICE) -P $(PORT) -U lfuse:w:$(LFU):m -U hfuse:w:$(HFU):m -U efuse:w:$(EFU):m

flash: ${BIN}.hex
	$(AVRDUDE) -F -V -c $(PROGRAMMER) -p $(DEVICE) -P $(PORT) -U flash:w:$<

clean:
	rm -f ${BIN}.elf ${BIN}.hex ${OBJS}

%.s: %.c
	${CC} ${CFLAGS} -S -o $@ $<
