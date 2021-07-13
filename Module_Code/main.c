#include <avr/io.h>
#include <util/delay.h>
#include "uart.h"
#include "fifo.h"
#include "ws2812b.h"
#include <avr/interrupt.h>

#define RET_EN_DDR                  DDRB
#define RET_EN_PORT                 PORTB
#define RET_EN_PIN                  0

#define MESSAGE_MAGIC               0xab    // Magic word used to mark the beginning of a message

#define MESSAGE_TYPE_RET_RST        0x00    // Reset own address, disable return path (RETO, ~RET_EN), always a broadcast message, len=0
#define MESSAGE_TYPE_ADDR           0x02    // Address idication for this module, len=1 (new address), enable return path, ack, disable return path
#define MESSAGE_TYPE_RET_SET        0x01    // Enable the return path (RETO, ~RET_EN), len=0
#define MESSAGE_TYPE_PING           0x10    // Ping message, response with an ACK
#define MESSAGE_TYPE_STAT           0x20    // Display a status value with the LEDs, len=1
#define MESSAGE_TYPE_DEL            0x30    // Delete the flash, len=0
#define MESSAGE_TYPE_DATA           0x31    // Next data block, len=1..256
#define MESSAGE_TYPE_PREP           0x40    // All data transmitted to modules, prepare for trigger, len=0
#define MESSAGE_TYPE_ACK            0xf0    // ACK last message (also used as pong), len=0
#define MESSAGE_TYPE_NACK           0xf1    // NACK last message, len=0

#define MESSAGE_ADDR_BROADCAST      0xff   // Broadcast address, interprete and redirect to the next one
#define MESSAGE_ADDR_HOST           0xfe   // Host address

#define MESSAGE_MAX_DATA_SIZE       256

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
    uint8_t data[MESSAGE_MAX_DATA_SIZE];
} __attribute__((packed)) message_t;

#define MESSAGE_HEADER_SIZE ((sizeof(message_t)-MESSAGE_MAX_DATA_SIZE))

void message_tx(message_t* msg)
{
    uint8_t* msg_raw = (uint8_t*)msg;
    for(uint8_t k = 0; k < MESSAGE_HEADER_SIZE; k++)
        uart_putc(msg_raw[k]);
    for(uint16_t k = 0; k < msg->len; k++)
        uart_putc(msg->data[k]);
}

void process_message(message_t* msg);
void transmit_response(message_t*msg, uint8_t success);
void display_status(uint8_t status);

int main()
{
    // Init GPIOs
    RET_EN_DDR |= (1<<RET_EN_PIN);

    ws2812b_init();
    uart_init();
    sei();

    // Send test data to LEDs
    /*uint8_t led_data[3*8];
    for(uint8_t k = 0; k < 8; k++)
    {
        led_data[k*3+0] = 0;
        led_data[k*3+1] = 85;
        led_data[k*3+2] = 170;
    }
    while(1)
    {
        ws2812b_send_column(led_data, 8);
        _delay_ms(5);
        for(uint8_t k = 0; k < 3*8; k++)
            led_data[k]++;
    }*/

    message_t msg;  // message buffer
    uint8_t counter = 0;
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
        {
            continue;
        }

        // Read the data
        for(uint16_t k = 0; k < msg.len; k++)
            msg.data[k] = fifo_popc_block(&uart_in_fifo);

        // Got a complete message
        if(msg.dst == MESSAGE_ADDR_BROADCAST || msg.dst != module_addr)
        {
            // This message is not for this module or is a broadcast message
            // Forward it to the next module
            message_tx(&msg);
        }

        if(msg.dst == module_addr || msg.dst == MESSAGE_ADDR_BROADCAST)
        {
            // This is a message for this module, process it
            process_message(&msg);
        }
    }
}

void process_message(message_t* msg)
{
    uint8_t status;
    switch(msg->type)
    {
    case MESSAGE_TYPE_RET_RST:
        if(msg->len != 0)
            return transmit_response(msg, 0);
        // Reset module address to 0
        module_addr = 0;
        // Disable the RETO transmitter, we don't know how many modules are after us
        RET_EN_PORT |= (1<<RET_EN_PIN);
        break;
    case MESSAGE_TYPE_ADDR:
        if(msg->len != 1)
            return transmit_response(msg, 0);
        // Set the current module address
        module_addr = msg->data[0];
        break;
    case MESSAGE_TYPE_RET_SET:
        if(msg->len != 0)
            return transmit_response(msg, 0);
        // Enable the RETO transmitter
        RET_EN_PORT &= ~(1<<RET_EN_PIN);
        break;
    case MESSAGE_TYPE_PING:
        // Fall through to send ACK
        break;
    case MESSAGE_TYPE_STAT:
        if(msg->len != 1)
            return transmit_response(msg, 0);
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
    transmit_response(msg, 1);
}

void transmit_response(message_t*msg, uint8_t success)
{
    msg->magic = MESSAGE_MAGIC;
    msg->type = success?MESSAGE_TYPE_ACK:MESSAGE_TYPE_NACK;
    msg->len = 0;
    msg->dst = MESSAGE_ADDR_HOST;
    msg->src = module_addr;
    message_tx(msg);
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
