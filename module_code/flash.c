#include "flash.h"
#include "uart.h"
#include <util/delay.h>
#include <avr/io.h>

// This flash control is for the Winbond W25Q16JV, but many others may be compatible
// Note: The actual application will not interface directly with the API in
// this file. Instead the wrapper in flash_sm is used, which will manage the
// automatic deletion of unused flash areas and things like that.

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

    // Set up SPI output pins
    FLASH_MOSI_DDR |= (1<<FLASH_MOSI_PIN);
    FLASH_SCK_DDR |= (1<<FLASH_SCK_PIN);
    FLASH_SS_DDR |= (1<<FLASH_SS_PIN);
	
	// Set up for SPI mode 0, master, f_sys/2
	SPCR = (1<<SPE) | (1<<MSTR);
    SPSR = (1<<SPI2X);

    // Reset the flash chip
    flash_reset();
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
	SPDR = 0xff;
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

uint8_t flash_status2()
{
	flash_select();
	flash_write(0x35);
	uint8_t status = flash_read();
	flash_deselect();
	return status;
}

void flash_reset()
{
    // Enable reset
    flash_select(),
    flash_write(0x66);
    flash_deselect();

    // Reset
    flash_select(),
    flash_write(0x99);
    flash_deselect();

    // Wait for the reset to finish
    _delay_us(100);
}

uint8_t flash_jedec_id()
{
    flash_select();
    flash_write(0x9f);
    uint8_t id = flash_read();
    flash_deselect();
    return id;
}

uint8_t flash_busy()
{
    return !!(flash_status() & FLASH_STATUS1_BUSY);
}

// Wait for the busy flag to clear
void flash_wait()
{
	while(flash_busy());
}

// Send write enable command
void flash_write_enable()
{
    flash_select();
    flash_write(0x06);
    flash_deselect();
}

void flash_sector_erase(uint16_t page)
{
    flash_write_enable();

    flash_select();
    flash_write(0x20);
    flash_write((page>>8)&0xff);    // Write page number (= address>>8)
    flash_write(page&0xff);
    flash_write(0x00);              // Lowest address byte is always 0, as we want to write a complete page
    flash_deselect();
}

// Erase the complete chip, will return once its done
void flash_chip_erase()
{
    flash_write_enable();

	flash_select();
	flash_write(0xC7);
	flash_deselect();
}

// Write a full page of 256 bytes into page number "page"
void flash_write_page(uint16_t page, uint8_t* data)
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
}

// Read a complete page from the flash, identified by the page number
void flash_read_page(uint16_t page, uint8_t* data)
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

// Start continuous read from zero address
void flash_read_cont_start(uint16_t page)
{
    flash_select();
    flash_write(0x03);              // Write read instruction
    flash_write((page>>8)&0xff);    // Write page number (= address>>8)
    flash_write(page&0xff);
    flash_write(0x00);              // Lowest address byte is always 0, as we want to read a complete page
}

// Read a block of cnt bytes in continuous mode
void flash_read_cont_read(uint8_t* data, uint8_t size)
{
    for(uint8_t i = 0; i < size; i++)
        data[i] = flash_read();
}

// Stop continuous read
void flash_read_cont_stop()
{
	flash_deselect();
}

void flash_suspend()
{
    flash_select();
    flash_write(0x75);
    flash_deselect();

    // The suspend needs up to 20us to finish - we just block here
    _delay_us(20);
}

void flash_resume()
{
    // Check if suspend bit is set
    if(!(flash_status2() & FLASH_STATUS2_SUS))
        return;
    flash_select();
    flash_write(0x7a);
    flash_deselect();

    // It is not allowed to issue another suspend within the next 20us, so we block
    // here 20us to make sure this will never happen
    _delay_us(20);
}
