#include "ws2812b.h"
#include <util/delay.h>

// This helps a lot to understand/lern this assembly stuff:
// https://rn-wissen.de/wiki/index.php?title=Inline-Assembler_in_avr-gcc

void ws2812b_init()
{
    WS2812B_DDR |= (1<<WS2812B_PIN);
}

// Play back a full column of pixel data
// Make sure that NO ISR is fired while this function runs, it will
// interrupt the playback and the LEDs may do crazy stuff.
void ws2812b_send_column(uint8_t* data_ptr, uint8_t led_cnt)
{
    // Prepare the high and low value used during playback
    uint8_t port_low  = WS2812B_PORT & ~(1<<WS2812B_PIN);
    uint8_t port_high = WS2812B_PORT |  (1<<WS2812B_PIN);
    // 1: 800ns high, 450ns low
    // 0: 400ns high, 850ns low
    uint8_t byte_cnt = led_cnt*3;
    asm volatile(
        "ld r18, %a[data_ptr]+;\n\t"     // r18 = current data value
        ".send_column_loop:\n\t"
        // bit 7
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 7\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 6
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 6\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 5
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 5\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 4
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 4\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 3
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 3\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 2
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 2\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t" "nop\n\t"
        // bit 1
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 1\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" "nop\n\t"
        "out 0x05,%[port_low]\n\t"
        "nop\n\t" //"nop\n\t" "nop\n\t"
        "ld r19, %a[data_ptr]+\n\t"         // 2 cycles, r19 = new data
        // bit 0
        "out 0x05,%[port_high]\n\t"
        "nop\n\t"
        "sbrs r18, 0\n\t"
        "out 0x05,%[port_low]\n\t"
        //"nop\n\t" //"nop\n\t"
        "mov r18, r19\n\t"                  // 1 cycle, Move new data to data register
        "dec %[byte_cnt]\n\t"               // 1 cycle, sets zero bit, if loop couter is zero, out will not change zero bit
        "out 0x05,%[port_low]\n\t"
        //"nop\n\t" "nop\n\t" "nop\n\t"
        "breq .send_column_loop_end\n\t"    // 1 cycle if no branch
        "rjmp .send_column_loop\n\t"        // 2 cycles
        ".send_column_loop_end:\n\t"

        :                                   // No output variables
        : [data_ptr] "e" (data_ptr),        // Data pointer as input
          [byte_cnt] "e" (byte_cnt),        // Number of bytes as input -> loop counter variable
          [port_low] "r" (port_low),        // low value for the port
          [port_high] "r" (port_high)       // high value for the port
        : "r18", "r19"        // clobber registers
        );
}

void ws2812b_trigger()
{
	WS2812B_CLR();
	//_delay_us(55);
}
