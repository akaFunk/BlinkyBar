#ifndef UART_H
#define UART_H

#include <stdint.h>
#include "fifo.h"

#define UART_UBRR_CALC(BAUD_,FREQ_) ((FREQ_)/((BAUD_)*8L)-1)
#define UART_BAUD_RATE 1000000L

extern fifo_t uart_in_fifo;

void uart_init();

void uart_putc(uint8_t buchstabe);
void uart_putcc(const char* String);
void uart_puti(uint32_t zahl);
void uart_putd(double Data);

#endif
