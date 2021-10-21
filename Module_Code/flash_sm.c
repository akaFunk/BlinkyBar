/*
Flash State Machine
As the erase progress for a full image might be quite long, this file implements
the elegant solution. The unused flash area will be erased while the flash has
nothing better to do. If there is a new page of data from the host to be written
to the flash, these functions will pause a current erase process, write the data
and resume the erase if required. If there is not space left, a page will be
erased and the data is written.
*/

#include "config.h"
#include "flash_sm.h"
#include "flash.h"
#include "uart.h"
#include <stdbool.h>

#define FLASH_PAGES         65536           // Number of pages (256 bytes) the flash provides
#define PAGES_PER_SECTOR    16              // Number of pages per sector

// State of the state machine
bool erasing;                               // True if there is currently an erase in progress
bool reading;                               // True if the flash is currently in continuous read mode
uint16_t image_start;                       // Page number where the current image starts
uint16_t image_length_page;                 // Length of the current image, given in number of pages
uint16_t image_length_columns;              // Length of the current image, given in number of columns
uint16_t image_extra_bytes;                 // Number of bytes which are currently in the flash, which do not make a full column
uint16_t image_columns_read;                // Number of columns already read - for wrap around function
uint16_t erase_next;                        // Page number of the next sector to erase

void flash_sm_init()
{
    erasing = false;
    reading = false;
    image_start = 0;
    image_length_page = 0;
    image_length_columns = 0;
    image_extra_bytes = 0;

    // Erase the first sector
    flash_sector_erase(image_start);
    
    // Wait for the erase to actually finish, then set erase_next
    flash_wait();
    erase_next = PAGES_PER_SECTOR;

    // Start the erase of the second sector
    flash_sm_erase_next();
}

void flash_sm_tick()
{
    // If we are currently reading, stop it
    if(reading)
        flash_sm_read_image_stop();
    
    // If we are currently erasing, check if that is done
    if(erasing && !flash_busy())
    {
        erasing = false;
        erase_next += PAGES_PER_SECTOR;  // The potential overflow is intended
    }
    // If we are currently not erasing, start the next erase
    if(!erasing)
        flash_sm_erase_next();
}

void flash_sm_erase_next()
{
    // Check if everything is erased and cancel in that case
    if(erase_next == image_start)
        return;
    flash_sector_erase(erase_next);
    erasing = true;
}

// Start a new image
void flash_sm_image_new()
{
    image_start += image_length_page;  // The potential overflow is intended
    image_length_page = 0;
    image_length_columns = 0;
    image_extra_bytes = 0;
}

void flash_sm_erase_wait()
{
    flash_wait();
    erasing = false;
    erase_next += PAGES_PER_SECTOR;  // The potential overflow is intended
}

// Append a full page to the current image
// Size must be 256 (one page) for all calls to this function, except the last
// one for an image. Nevertheless, we always write 256 and accept garbage data
// in the last page of the image.
void flash_sm_image_append(uint8_t* data, uint16_t size)
{
    // If we are currently reading image data, stop it
    if(reading)
        flash_sm_read_image_stop();

    // Make sure that there is no erase process and that there is enough free space.
    // If there is not enough space, wait for the erase process to finish, otherwise
    // suspend it. If There is not enough space and there is currently no erase process
    // running, start a new one and wait for it to finish.
    uint16_t page = image_start + image_length_page;
    bool enough_space = page != erase_next;

    if(!enough_space && erasing)
    {
        flash_sm_erase_wait();

        // Write the data
        flash_write_page(page, data);
        flash_wait();
    }
    else if(!enough_space && !erasing)
    {
        // Start a new erase and wait for it to finish
        flash_sm_erase_next();
        flash_sm_erase_wait();

        // Write the data
        flash_write_page(page, data);
        flash_wait();
    }
    else if(enough_space && erasing)
    {
        // Pause the erase
        flash_suspend();

        // Write the data and wait for completion
        flash_write_page(page, data);
        flash_wait();

        // Resume erase
        flash_resume();
    }
    else if(enough_space && !erasing)
    {
        // Just write the data and wait for completion
        flash_write_page(page, data);
        flash_wait();
    }
    image_length_page++;
    image_extra_bytes += size;
    while(image_extra_bytes >= LED_COUNT*3)
    {
        image_length_columns++;
        image_extra_bytes -= LED_COUNT*3;
    }
}

void flash_sm_print_state()
{
    uart_putcc("image_start: ");
    uart_putu32(image_start);
    uart_putcc(", image_length_page: ");
    uart_putu32(image_length_page);
    uart_putcc(", image_length_columns: ");
    uart_putu32(image_length_columns);
    uart_putcc(", image_extra_bytes: ");
    uart_putu32(image_extra_bytes);
    uart_putcc(", erasing: ");
    uart_putb(erasing);
    uart_putcc(", reading: ");
    uart_putb(reading);
    uart_putcc(", erase_next: ");
    uart_putu32(erase_next);
    uart_putcc(", busy: ");
    if(!reading)
        uart_putb(!!flash_busy());
    else
        uart_putc('?');
    uart_putcc("\n");
}

// Start a new read process
void flash_sm_read_image_start()
{
    // If we are already in reading mode, stop it first
    if(reading)
        flash_sm_read_image_stop();

    // If we are currently erasing, pause it
    if(erasing)
        flash_suspend();
    // We keep erasing true if it was true, as it is used by flash_sm_read_image_stop()
    // to determine if an erase process has to be continued.

    // Start continuous mode
    flash_read_cont_start(image_start);
    reading = true;
    image_columns_read = 0;
}

// Read next column in continuous flash read mode
void flash_sm_read_image_data(uint8_t* data, uint8_t size)
{
    // Make sure we are in continuous read mode
    if(!reading)
        return;
    
    // Check for wraparound and restart read
    if(image_columns_read == image_length_columns)
        flash_sm_read_image_start();

    // Read the data
    flash_read_cont_read(data, size);
    image_columns_read++;
}

// Stop the image read process and put flash back into normal operation.
// This function is not called by the API of the module. It will be called
// automatically if any other flash operation except for reading data is
// issued.
void flash_sm_read_image_stop()
{
    if(!reading)
        return;
    
    // Stop continuous read mode
    flash_read_cont_stop();
    reading = false;

    // Resume erase process, if it was running when switching into continuous mode
    if(erasing)
        flash_resume();
}
