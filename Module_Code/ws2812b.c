#include "ws2812b.h"
#include <util/delay.h>

void ws2812b_init()
{
    WS2812B_DDR |= (1<<WS2812B_PIN);
}

void ws2812b_send_column(uint8_t* data_ptr, uint8_t led_cnt)
{
    // 1: 800ns high, 450ns low
    // 0: 400ns high, 850ns low
    uint8_t byte_cnt = led_cnt*3;
    asm volatile(
        "ldi r16,0x00\n\t"               // r16 = 0 port value
        "ldi r17,0x02\n\t"               // r17 = 1 port value
        "ld r18, %a[data_ptr]+;\n\t"     // r18 = current data value
        ".send_column_loop:\n\t"
        // bit 7
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 7\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 6
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 6\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 5
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 5\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 4
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 4\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 3
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 3\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 2
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 2\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 1
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 1\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,r16\n\t"
        "nop\n\t" //"nop\n\t" "nop\n\t"
        "ld r19, %a[data_ptr]+\n\t"         // 2 cycles, r19 = new data
        // bit 0
        "out 0x05,r17\n\t"
        "nop\n\t"
        "sbrs r18, 0\n\t"
        "out 0x05,r16\n\t"
        //"nop\n\t" //"nop\n\t"
        "mov r18, r19\n\t"                  // 1 cycle, Move new data to data register
        "dec %[byte_cnt]\n\t"               // 1 cycle, sets zero bit, if loop couter is zero, out will not change zero bit
        "out 0x05,r16\n\t"
        //"nop\n\t" "nop\n\t" "nop\n\t"
        "breq .send_column_loop_end\n\t"    // 1 cycle if no branch
        "rjmp .send_column_loop\n\t"        // 2 cycles
        ".send_column_loop_end:\n\t"

        :                                   // No output variables
        : [data_ptr] "e" (data_ptr),        // Data pointer as input
          [byte_cnt] "e" (byte_cnt)         // Number of bytes as input -> loop counter variable
        : "r16", "r17", "r18", "r19"        // clobber registers
        );
}

void ws2812b_trigger()
{
	WS2812B_CLR();
	_delay_us(200);
}
