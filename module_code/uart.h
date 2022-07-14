#ifndef UART_H
#define UART_H

#include <stdint.h>
#include <stdbool.h>
#include "fifo.h"

#define UART_UBRR_CALC(BAUD_,FREQ_) ((FREQ_)/((BAUD_)*8L)-1)
#define UART_BAUD_RATE 500000UL

extern fifo_t uart_in_fifo;

void uart_init();

void uart_putc(uint8_t data);
void uart_putcc(const char* string);
void uart_putu32(uint32_t number);
void uart_putb(bool num);

#endif
