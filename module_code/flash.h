#ifndef _FLASH_H
#define _FLASH_H

#include <avr/io.h>

#define FLASH_CS_DDR        DDRD
#define FLASH_CS_PORT       PORTD
#define FLASH_CS_PIN        4

#define FLASH_WP_DDR        DDRD
#define FLASH_WP_PORT       PORTD
#define FLASH_WP_PIN        3

#define FLASH_HOLD_DDR      DDRD
#define FLASH_HOLD_PORT     PORTD
#define FLASH_HOLD_PIN      2

#define FLASH_MOSI_DDR      DDRB
#define FLASH_MOSI_PIN      3

#define FLASH_SCK_DDR       DDRB
#define FLASH_SCK_PIN       5

// Unused SS pin, but needs to be set as output
#define FLASH_SS_DDR        DDRB
#define FLASH_SS_PIN        2

#define FLASH_STATUS1_BUSY  0x01


void flash_init();

#define flash_select() FLASH_CS_PORT &= ~(1<<FLASH_CS_PIN)
#define flash_deselect() FLASH_CS_PORT |= (1<<FLASH_CS_PIN)

void flash_write(uint8_t data);
uint8_t flash_read();
uint8_t flash_status();
void flash_reset();
uint8_t flash_jedec_id();
uint8_t flash_busy();
void flash_wait();
void flash_write_enable();
void flash_sector_erase(uint16_t page);
void flash_chip_erase();
void flash_write_page(uint16_t page, uint8_t* data);
void flash_read_page(uint16_t page, uint8_t* data);

// Continuous read functions
void flash_read_cont_start(uint16_t page);
void flash_read_cont_read(uint8_t* data, uint8_t size);
void flash_read_cont_stop();

// Suspend/Resume program/erase
void flash_suspend();
void flash_resume();

#endif
