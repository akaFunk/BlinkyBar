#include "flash_sm.h"
#include "flash.h"
#include <stdbool.h>

#define FLASH_PAGES         65536           // Number of pages (256 bytes) the flash provides
#define PAGES_PER_SECTOR    16              // Number of pages per sector

// State of the state machine
bool erasing;                               // True if there is currently an erase in progress
uint16_t image_start;                       // Page number where the current image starts
uint16_t image_length;                      // Length of the current image, given in number of pages
uint16_t erase_next;                        // Page number of the next page to erase

void flash_sm_init()
{
    erasing = false;
    image_start = 0;
    image_length = 0;

    // Erase the first sector
    flash_sector_erase(image_start);
    
    // Wait for the erase to actually finish, then increment page_free
    flash_wait();
    erase_next = PAGES_PER_SECTOR;
}

void flash_sm_tick()
{
    // If we are currently erasing, check if that is done
    if(erasing && !flash_busy())
    {
        erasing = false;
        erase_next += PAGES_PER_SECTOR;
        flash_sm_erase_next();
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
    image_start += image_length;
    image_length = 0;
}

void flash_sm_erase_wait()
{
    flash_wait();
    erasing = false;
}

// Append a full page to the current image
void flash_sm_image_append(uint8_t* data)
{
    // Make sure that there is no erase process and that there is enough free space
    // If there is not enough space, wait for the erase process to finish, otherwise
    // suspend it. If There is not enough space and there is currently no erase process
    // running, start a new one and wait for it to finish.
    bool enough_space = image_start + image_length != erase_next;

    if(!enough_space && erasing)
    {
        flash_sm_erase_wait();

        // Write the data
        flash_write_page(image_start + image_length, data);
        image_length++;
        flash_wait();
    }
    else if(!enough_space && !erasing)
    {
        // Start a new erase and wait for it to finish
        flash_sm_erase_next();
        flash_sm_erase_wait();

        // Write the data
        flash_write_page(image_start + image_length, data);
        image_length++;
        flash_wait();
    }
    else if(enough_space && erasing)
    {
        // Pause the erase
        flash_suspend();

        // Write the data and wait for completion
        flash_write_page(image_start + image_length, data);
        image_length++;
        flash_wait();

        // Resume erase
        flash_resume();
    }
    else if(enough_space && !erasing)
    {
        // Just write the data and wait for completion
        flash_write_page(image_start + image_length, data);
        image_length++;
        flash_wait();
    }
}
