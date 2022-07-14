#ifndef _FLASH_SM_H
#define _FLASH_SM_H

#include <stdint.h>

void flash_sm_init();
void flash_sm_tick();
void flash_sm_erase_next();
void flash_sm_image_new();
void flash_sm_erase_wait();
void flash_sm_image_append(uint8_t* data, uint16_t size);
void flash_sm_print_state();
void flash_sm_read_image_start();
void flash_sm_read_image_data(uint8_t* data, uint8_t size);
void flash_sm_read_image_stop();

#endif
