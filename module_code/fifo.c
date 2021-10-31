#include "fifo.h"
#include <avr/interrupt.h>

void fifo_init(fifo_t* fifo, uint16_t size, uint8_t* data)
{
	fifo->data = data;
	fifo->rptr = data;
	fifo->wptr = data;
	fifo->used = 0;
	fifo->size = size;
	fifo->end = data + size;
}

void fifo_pushc(fifo_t* fifo, uint8_t data)
{
	cli();
	if(fifo->used >= fifo->size)
	{
		sei();
		return;
	}
	fifo->used++;
	*fifo->wptr = data;
	fifo->wptr++;
	if(fifo->wptr == fifo->end)
		fifo->wptr = fifo->data;
	sei();
}

void fifo_pushcc(fifo_t* fifo, uint8_t* data, uint16_t length)
{
    for(uint16_t i = 0; i < length; i++)
        fifo_pushc(fifo, data[i]);
}

uint8_t fifo_popc(fifo_t* fifo)
{
	uint8_t data;
	cli();
	if(!fifo->used)
	{
		sei();
		return 0;
	}
	data = *fifo->rptr;
	fifo->used--;
	fifo->rptr++;
	if(fifo->rptr == fifo->end)
		fifo->rptr = fifo->data;
	sei();
	return data;
}

uint8_t fifo_popc_block(fifo_t* fifo)
{
	while(!fifo_used(fifo));
	return fifo_popc(fifo);
}

void fifo_popcc(fifo_t* fifo, uint8_t* data, uint16_t length)
{
    for(uint16_t i = 0; i < length; i++)
        data[i] = fifo_popc(fifo);
}

// Read a character at a given position pos without removing it from
// the buffer
extern uint8_t fifo_readc(fifo_t* fifo, uint16_t pos)
{
	cli();
	uint8_t* ptr = fifo->rptr+pos;
	if(ptr >= fifo->end)
		ptr -= fifo->size;
	if(!fifo->used)
	{
		sei();
		return 0;
	}
	sei();
	return *ptr;
}

uint16_t fifo_used(fifo_t* fifo)
{
	uint16_t used;
	cli();
	used = fifo->used;
	sei();
	return used;
}

uint16_t fifo_free(fifo_t* fifo)
{
    return fifo->size - fifo_used(fifo);
}
