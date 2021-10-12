#include <avr/io.h>
#include <util/delay.h>
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
#define MESSAGE_TYPE_DEL            0x40    // Delete the flash, len=0
#define MESSAGE_TYPE_DATA           0x41    // Next data block, len=1..256
#define MESSAGE_TYPE_PREP           0x50    // All data transmitted to modules, prepare for trigger, len=0
#define MESSAGE_TYPE_ACK            0xf0    // ACK last message (also used as pong), len=0
#define MESSAGE_TYPE_NACK           0xf1    // NACK last message, len=0

#define MESSAGE_ADDR_BROADCAST      0xff   // Broadcast address, interprete and redirect to the next one
#define MESSAGE_ADDR_HOST           0xfe   // Host address

#define MESSAGE_MAX_DATA_SIZE       256    // Maximum length of data in a message

uint8_t module_addr = 0x00;  // Address of this module

// Examples:
// Set address 0 -> 1: ab02fe00010001
// Ping 1:             ab10fe010000
// Ping 0:             ab10fe000000

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

int main()
{
    // Init GPIOs
    RET_EN_PORT |= (1<<RET_EN_PIN);  // Disable return path by default
    RET_EN_DDR |= (1<<RET_EN_PIN);
    PWR_EN_PORT &= (1<<PWR_EN_PIN);  // Disable own power supply by default
    PWR_EN_DDR |= (1<<PWR_EN_PIN);
    LED_DDR |= (1<<LED_PIN);

    // Before we do anything, we wait 2 seconds, then turn on the power supply for ourself
    _delay_ms(2000);
    PWR_EN_PORT |= (1<<PWR_EN_PIN);

    ws2812b_init();
    uart_init();
    flash_init();
    sei();

    // TODO: Shutdown ALL LEDs
    display_status(0);

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

        // Got a complete message, interprete it
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
        return;  // don't send an ACK
    case MESSAGE_TYPE_RET_ENABLE:
        if(msg->len != 0)
            return transmit_response(0);
        // Enable the RET* transmitter
        RET_EN_PORT &= ~(1<<RET_EN_PIN);
        display_status(4);
        return;  // don't send an ACK
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
    case MESSAGE_TYPE_DEL:
        // TODO: Delete the flash
        break;
    case MESSAGE_TYPE_DATA:
        // TODO: Copy data to flash
        break;
    case MESSAGE_TYPE_PREP:
        // TODO: Copy first row from flash
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
