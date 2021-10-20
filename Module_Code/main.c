#include <avr/io.h>
#include <util/delay.h>
#include "config.h"
#include "uart.h"
#include "fifo.h"
#include "ws2812b.h"
#include "flash.h"
#include "flash_sm.h"
#include <avr/interrupt.h>
#include <avr/io.h>
#include <string.h>

#define RET_EN_DDR                  DDRB
#define RET_EN_PORT                 PORTB
#define RET_EN_PIN                  0

#define PWR_EN_DDR                  DDRC
#define PWR_EN_PORT                 PORTC
#define PWR_EN_PIN                  4

#define LED_DDR                     DDRC
#define LED_PORT                    PORTC
#define LED_PIN                     2
#define led_on()                    LED_PORT |= (1<<LED_PIN)
#define led_off()                   LED_PORT &= ~(1<<LED_PIN)
#define led_toggle()                LED_PORT ^= (1<<LED_PIN)

#define MESSAGE_MAGIC               0xab    // Magic word used to mark the beginning of a message

#define MESSAGE_TYPE_ADDR_SET       0x00    // Set a new module address, len=1 (new address), no ACK
#define MESSAGE_TYPE_RET_DISABLE    0x10    // Disable the return path, len=0, no ACK
#define MESSAGE_TYPE_RET_ENABLE     0x11    // Enable the return path, len=0, no ACK
#define MESSAGE_TYPE_PING           0x20    // Ping message, response with an ACK
#define MESSAGE_TYPE_STAT           0x30    // Display a status value with the LEDs, len=1
#define MESSAGE_TYPE_IMG_NEW        0x40    // Start storing a new image, len=0
#define MESSAGE_TYPE_IMG_APP        0x41    // Next image data block, len=1..256, must be 256 for all messages except the last one for an image
#define MESSAGE_TYPE_PREP           0x50    // All data transmitted to modules, prepare for trigger, len=0
#define MESSAGE_TYPE_TRIG           0x51    // Trigger a column - just for debug purposes, normal operation though TRIGI signal interrupt
#define MESSAGE_TYPE_ACK            0xf0    // ACK last message (also used as pong), len=0
#define MESSAGE_TYPE_NACK           0xf1    // NACK last message, len=0

#define MESSAGE_ADDR_BROADCAST      0xff   // Broadcast address, interpret and redirect to the next one
#define MESSAGE_ADDR_HOST           0xfe   // Host address

#define MESSAGE_MAX_DATA_SIZE       256    // Maximum length of data in a message

uint8_t module_addr =               0x00;  // Address of this module
uint8_t rgb_data[3*LED_COUNT];             // Buffer for next LED column
uint16_t current_column =           0;     // Current column index

typedef struct
{
    uint8_t magic;
    uint8_t type;
    uint8_t src;
    uint8_t dst;
    uint16_t len;
} __attribute__((packed)) message_header_t;

typedef struct
{
    uint8_t magic;
    uint8_t type;
    uint8_t src;
    uint8_t dst;
    uint16_t len;
    uint8_t data[MESSAGE_MAX_DATA_SIZE];
} __attribute__((packed)) message_t;

#define MESSAGE_HEADER_SIZE ((sizeof(message_t)-MESSAGE_MAX_DATA_SIZE))

void message_tx(message_t* msg)
{
    uint8_t* msg_raw = (uint8_t*)msg;
    for(uint8_t k = 0; k < MESSAGE_HEADER_SIZE + msg->len; k++)
        uart_putc(msg_raw[k]);
}

void process_message(message_t* msg);
void transmit_response(uint8_t success);
void display_status(uint8_t status);
void debug_flash();
void debug_flash_sm();

int main()
{
    // Init GPIOs
    RET_EN_PORT |= (1<<RET_EN_PIN);  // Disable return path by default
    RET_EN_DDR |= (1<<RET_EN_PIN);
    PWR_EN_PORT &= (1<<PWR_EN_PIN);  // Disable own power supply by default
    PWR_EN_DDR |= (1<<PWR_EN_PIN);
    LED_DDR |= (1<<LED_PIN);

    // Before we do anything, we wait 2 seconds, then turn on the power supply for ourself
    _delay_ms(200);  // TODO: Reset to ~2000
    PWR_EN_PORT |= (1<<PWR_EN_PIN);

    ws2812b_init();
    uart_init();
    flash_init();
    sei();

    // TODO: Shutdown ALL LEDs
    display_status(0);

    // Test flash
    //debug_flash()

    // Test flash state machine
    //debug_flash_sm();

    message_t msg;  // message buffer
    //uint8_t counter = 0;
    while(1)
    {
        // Wait for the magic word
        while(fifo_popc_block(&uart_in_fifo) != MESSAGE_MAGIC);
        msg.magic = MESSAGE_MAGIC;

        // Read the rest of the header, exclude magic word
        uint8_t* header = ((uint8_t*)&msg) + 1;
        for(uint8_t k = 0; k < MESSAGE_HEADER_SIZE - 1; k++)
            header[k] = fifo_popc_block(&uart_in_fifo);

        // Check data length
        if(msg.len > MESSAGE_MAX_DATA_SIZE)
            continue;

        // Read the data
        for(uint16_t k = 0; k < msg.len; k++)
            msg.data[k] = fifo_popc_block(&uart_in_fifo);

        // Got a complete message, interpret it
        if(msg.dst == module_addr || msg.dst == MESSAGE_ADDR_BROADCAST)
            process_message(&msg);

        // If this message is not for this module or is a broadcast message,
        // forward it to the next module
        if(msg.dst == MESSAGE_ADDR_BROADCAST || msg.dst != module_addr)
            message_tx(&msg);
    }
}

void process_message(message_t* msg)
{
    uint8_t status;
    switch(msg->type)
    {
    case MESSAGE_TYPE_ADDR_SET:
        if(msg->len != 1)
            return transmit_response(0);
        // Set the current module address
        module_addr = msg->data[0];
        display_status(2);
        return;  // don't send ACK
    case MESSAGE_TYPE_RET_DISABLE:
        if(msg->len != 0)
            return transmit_response(0);
        // Disable the RET* transmitter, we don't know how many modules are after us
        RET_EN_PORT |= (1<<RET_EN_PIN);
        display_status(1);
        return;  // don't send an ACK, no one will get it anyways
    case MESSAGE_TYPE_RET_ENABLE:
        if(msg->len != 0)
            return transmit_response(0);
        // Enable the RET* transmitter
        RET_EN_PORT &= ~(1<<RET_EN_PIN);
        display_status(4);
        break;
    case MESSAGE_TYPE_PING:
        // Fall through to send ACK
        break;
    case MESSAGE_TYPE_STAT:
        if(msg->len != 1)
            return transmit_response(0);
        status = msg->data[0];
        // TODO: Send this status value to the LEDs
        display_status(status);
        break;
    case MESSAGE_TYPE_IMG_NEW:
        // Start a new image
        flash_sm_image_new();
        break;
    case MESSAGE_TYPE_IMG_APP:
        // Append new image data to the current image
        flash_sm_image_append(msg->data, msg->len);
        break;
    case MESSAGE_TYPE_PREP:
        // Put the flash in continuous read mode and read the first column
        flash_sm_read_image_start();
        flash_sm_read_image_data(rgb_data, LED_COUNT*3);
        break;
    case MESSAGE_TYPE_TRIG:
        // Send data to LEDs and load new data after that
        ws2812b_send_column(rgb_data, LED_COUNT);
        flash_sm_read_image_data(rgb_data, LED_COUNT*3);
        break;
    }

    // Transmit an ACK
    transmit_response(1);
}

void transmit_response(uint8_t success)
{
    message_header_t msg;
    msg.magic = MESSAGE_MAGIC;
    msg.type = success?MESSAGE_TYPE_ACK:MESSAGE_TYPE_NACK;
    msg.len = 0;
    msg.dst = MESSAGE_ADDR_HOST;
    msg.src = module_addr;
    message_tx((message_t*)&msg);
}

void display_status(uint8_t status)
{
    uint8_t status_led_data[3*8];
    for(uint8_t k = 0; k < 8; k++)
    {
        status_led_data[k*3+0] = ((status<<k)&0x80)>>2;
        status_led_data[k*3+1] = 0;
        status_led_data[k*3+2] = 0;
    }
    ws2812b_send_column(status_led_data, 8);
    _delay_ms(1);
}

void debug_flash_sm()
{
    // DEBUG - Test flash image write and automatic erase
    uint8_t data[256];
    RET_EN_PORT &= ~(1<<RET_EN_PIN);  // Enable return path for debug
    _delay_ms(200);  // wait a moment for the uart line to stabilize
    flash_sm_init();
    flash_sm_print_state();
    _delay_ms(100);
    flash_sm_print_state();
    flash_sm_tick();
    flash_sm_print_state();
    flash_sm_image_new();
    flash_sm_print_state();
    flash_sm_image_append(data, 256);
    flash_sm_print_state();
    flash_sm_image_new();
    flash_sm_print_state();
    flash_sm_image_append(data, 256);
    flash_sm_print_state();
    for(int i = 0; i < 33; i++)
        flash_sm_image_append(data, 256);
    flash_sm_print_state();
}

void debug_flash()
{
    uint8_t data[256];
    // DEBUG - Test flash block write and read process
    RET_EN_PORT &= ~(1<<RET_EN_PIN);  // Enable return path for debug
    uart_putcc("\r\nStarted\r\n");
    flash_chip_erase();
    uart_putcc("Chip erased\r\n");
    strcpy((char*)data, "Hello world!\r\n");
    flash_write_page(1, data);
    uart_putcc("Write done\r\n");
    for(int i = 0; i < 256; i++)
        data[i] = 'x';
    flash_read_cont_start(1);
    uart_putcc("Read started\r\n");
    while(1)
    {
        uint8_t data;
        flash_read_cont_read(&data, 1);
        if(data == 0 || data == 0xff)
            break;
        uart_putc(data);
    }
    flash_read_cont_stop();
    uart_putcc("Read done\r\n");
}
