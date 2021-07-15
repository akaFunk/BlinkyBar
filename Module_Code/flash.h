#ifndef _FLASH_H
#define _FLASH_H

#include <avr/io.h>

#define FLASH_CS_DDR DDRB
#define FLASH_CS_PORT PORTB
#define FLASH_CS_PIN 2

#define FLASH_WP_DDR        DDRD
#define FLASH_WP_PORT       PORTD
#define FLASH_WP_PIN        3

#define FLASH_HOLD_DDR      DDRD
#define FLASH_HOLD_PORT     PORTD
#define FLASH_HOLD_PIN      2

#define FLASH_STATUS1_BUSY  0x01


void flash_init();

#define flash_select() FLASH_CS_PORT &= ~(1<<FLASH_CS_PIN)
#define flash_deselect() FLASH_CS_PORT |= (1<<FLASH_CS_PIN)

void flash_write(uint8_t data);
uint8_t flash_read();
uint8_t flash_status();
void flash_wait();
void flash_write_enable();
void flash_chip_erase();
void flash_write_block(uint16_t page, uint8_t* data);
void flash_readBlock(uint16_t page, uint8_t* data);

// Continous read functions
void flash_read_cont_start();
void flash_read_cont_read(uint8_t cnt, uint8_t* data);
void flash_read_cont_stop();

#endif
