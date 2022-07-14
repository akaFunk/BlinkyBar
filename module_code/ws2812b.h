#include <avr/io.h>

#define WS2812B_DDR    DDRB
#define WS2812B_PORT   PORTB
#define WS2812B_PIN    1

#define WS2812B_SET()  WS2812B_PORT |=  (1<<WS2812B_PIN)
#define WS2812B_CLR()  WS2812B_PORT &= ~(1<<WS2812B_PIN)
//#define WS2812B_SET()  asm volatile("sbi 0x05,2")
//#define WS2812B_CLR()  asm volatile("cbi 0x05,2")

void ws2812b_init();
void ws2812b_send_column(uint8_t* data_ptr, uint8_t led_cnt);
void ws2812b_trigger();
