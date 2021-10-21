#include "uart.h"
#include <avr/interrupt.h>
#include <avr/io.h>
#include <stdlib.h>

#define UART_IN_SIZE    300
fifo_t uart_in_fifo;
uint8_t uart_in_fifo_data[UART_IN_SIZE];

void uart_init()
{
    // Initialize fifos
    fifo_init(&uart_in_fifo, UART_IN_SIZE, uart_in_fifo_data);

    // init baud rate
    UBRR0H = (uint8_t)(UART_UBRR_CALC(UART_BAUD_RATE, F_CPU) >> 8);
    UBRR0L = (uint8_t)(UART_UBRR_CALC(UART_BAUD_RATE, F_CPU));

    UCSR0B = (1<<TXEN0) | (1<<RXEN0) | (1<<RXCIE0);
    UCSR0C = (1<<UCSZ00) | (1<<UCSZ01);

    do
    {
        UDR0;
    } while (UCSR0A & (1 << RXC0));
    UCSR0A = (1 << RXC0) | (1 << TXC0) | (1<<U2X0);
}

ISR(USART_RX_vect)
{
    uint8_t data = UDR0;

    // Put data into fifo
    fifo_pushc(&uart_in_fifo, data);
}

void uart_putc(uint8_t data)
{
    while(!(UCSR0A & (1<<UDRE0)));
    UDR0 = data;
}

void uart_putcc(const char* string)
{
    while(*string)
    {
        uart_putc(*string);
        string++;
    }
}

void uart_putu32(uint32_t number)
{
    char s[7];
    utoa(number, s, 10);
    uart_putcc(s);
}

void uart_putb(bool num)
{
    if(num)
        uart_putc('1');
    else
        uart_putc('0');
}
