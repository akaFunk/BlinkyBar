#ifndef FIFO_H_
#define FIFO_H_

#include <stdint.h>

typedef struct
{
	uint16_t size;
	uint16_t used;
	uint8_t* rptr;
	uint8_t* wptr;
	uint8_t* data;
} fifo_t;

void fifo_init(fifo_t* fifo, uint16_t size, uint8_t* data);
void fifo_pushc(fifo_t* fifo, uint8_t data);
void fifo_pushcc(fifo_t* fifo, uint8_t* data, uint16_t length);
uint8_t fifo_popc(fifo_t* fifo);
void fifo_popcc(fifo_t* fifo, uint8_t* data, uint16_t length);
uint8_t fifo_readc(fifo_t* fifo, uint16_t pos);
uint16_t fifo_used(fifo_t* fifo);
uint16_t fifo_free(fifo_t* fifo);

#endif
