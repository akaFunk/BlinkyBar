#include "flash.h"
#include "uart.h"
#include <util/delay.h>

// This flash control is for the W25Q16JV

// Sets up hardware SPI interface and CS pin
void flash_init()
{
    // Set up CS
	flash_deselect();
	FLASH_CS_DDR |= (1<<FLASH_CS_PIN);

    // Set up WP and HOLD
    FLASH_WP_PORT |= (1<<FLASH_WP_PIN);
    FLASH_WP_DDR |= (1<<FLASH_WP_PIN);
    FLASH_HOLD_PORT |= (1<<FLASH_HOLD_PIN);
    FLASH_HOLD_DDR |= (1<<FLASH_HOLD_PIN);
	
	// Set up for SPI mode 0
	SPCR = (1<<SPE) | (1<<MSTR);
}

// Write a byte to the SPI
void flash_write(uint8_t data)
{
	SPDR = data;
	while(!(SPSR & (1<<SPIF)));
	SPDR;
}

// Read a byte from the SPI
uint8_t flash_read()
{
	SPDR = 0;
	while(!(SPSR & (1<<SPIF)));
	return SPDR;
}

// Reat the status1 register
uint8_t flash_status()
{
	flash_select();
	flash_write(0x05);
	uint8_t status = flash_read();
	flash_deselect();
	return status;
}

// Wait for the busy flag to clear
void flash_wait()
{
	while(flash_status() & FLASH_STATUS1_BUSY);
}

// Send write enable command
void flash_write_enable()
{
    flash_select();
    flash_write(0x06);
    flash_deselect();
}

// Erase the complete chip, will return once its done
void flash_chip_erase()
{
    flash_write_enable();

	flash_select();
	flash_write(0xC7);
	flash_deselect();
	
	flash_wait();  // Wait to finish operation
}

// Write a full page of 256 bytes into page number "page"
void flash_write_block(uint16_t page, uint8_t* data)
{
	uint16_t i;

    // Enable write
    flash_write_enable();

    flash_select();
    flash_write(0x02);              // Write page instruction
    flash_write((page>>8)&0xff);    // Write page number (= address>>8)
    flash_write(page&0xff);
    flash_write(0x00);              // Lowest address byte is always 0, as we want to write a complete page

    // Write data
	for(i=0; i<256; i++)
		flash_write(data[i]);

    flash_deselect();
	
	// Wait for data to be written
	flash_wait();
}

// Read a complete block from the flash, identified by the page number
void flash_read_block(uint16_t page, uint8_t* data)
{
	uint16_t i;

    flash_select();
    flash_write(0x03);              // Write read instruction
    flash_write((page>>8)&0xff);    // Write page number (= address>>8)
    flash_write(page&0xff);
    flash_write(0x00);              // Lowest address byte is always 0, as we want to write a complete page
	for(i=0; i<256; i++)
		data[i] = flash_read();     // Read the data
	flash_deselect();
}

// Start continous read from zero address
void flash_read_cont_start()
{
    flash_select();
    flash_write(0x03);              // Write read instruction
    flash_write(0x00);              // Address is 0
    flash_write(0x00);
    flash_write(0x00);
}

// Read a block of cnt bytes in continous mode
void flash_read_cont_read(uint8_t cnt, uint8_t* data)
{
    for(uint8_t i = 0; i < cnt; i++)
        data[i] = flash_read();
}

// Stop continous read
void flash_read_cont_stop()
{
	flash_deselect();
}
