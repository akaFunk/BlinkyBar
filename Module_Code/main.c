#include <avr/io.h>
#include <util/delay.h>
#include "uart.h"
#include <avr/interrupt.h>

int main()
{
    uart_init();
    sei();

    DDRB |= (1<<5);
    while(1)
    {
        PORTB ^= (1<<5);
        //_delay_ms(1000);
        //uart_putcc("Hello\r\n");
        while(!fifo_used(&uart_in_fifo));
        uint8_t data = fifo_popc(&uart_in_fifo);
        uart_putc(data);
    }
}
