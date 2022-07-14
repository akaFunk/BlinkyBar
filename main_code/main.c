#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <util/atomic.h>

#define MIN_VOLTAGE      6000   // minimum voltage (mV), below this value the module will turn itself off

#define LED_DDR          DDRC
#define LED_PORT         PORTC
#define LED_PIN          2
#define led_init()       LED_DDR |= (1<<LED_PIN)
#define led_on()         LED_PORT |= (1<<LED_PIN)
#define led_off()        LED_PORT &= ~(1<<LED_PIN)
#define led_toggle()     LED_PORT ^= (1<<LED_PIN)

#define PI_SHTDN_DDR     DDRC
#define PI_SHTDN_PORT    PORTC
#define PI_SHTDN_PIN     0
#define pi_shtdn_init()  PI_SHTDN_DDR |= (1<<PI_SHTDN_PIN)
#define pi_shtdn_low()   PI_SHTDN_PORT &= ~(1<<PI_SHTDN_PIN)
#define pi_shtdn_high()  PI_SHTDN_PORT |= (1<<PI_SHTDN_PIN)

#define MASTER_ON_DDR    DDRC
#define MASTER_ON_PORT   PORTC
#define MASTER_ON_VALUE  PINC
#define MASTER_ON_PIN    1
#define master_on_init() MASTER_ON_DDR &= ~(1<<MASTER_ON_PIN)
#define master_on_pu()   MASTER_ON_PORT |= (1<<MASTER_ON_PIN)
#define master_on_val()  (MASTER_ON_VALUE & (1<<MASTER_ON_PIN))

#define PWR_ON_DDR     DDRC
#define PWR_ON_PORT    PORTC
#define PWR_ON_PIN     3
#define pwr_on_init()  PWR_ON_DDR |= (1<<PWR_ON_PIN)
#define pwr_on_low()   PWR_ON_PORT &= ~(1<<PWR_ON_PIN)
#define pwr_on_high()  PWR_ON_PORT |= (1<<PWR_ON_PIN)

static uint8_t spi_byte_cnt = 0;

typedef struct __attribute__((__packed__)) {
    uint8_t command;
    uint16_t period;
    uint16_t on_time;
    uint16_t trigger_count;
} command_t;
static volatile command_t command_buffer;
static uint8_t *command_buffer_data = (uint8_t*)&command_buffer;
#define COMMAND_START_TRIGGER   0x01
#define COMMAND_STOP_TRIGGER    0x02
#define COMMAND_INFINITE_REPEAT 0x04

typedef struct __attribute__((__packed__)) {
    uint8_t magic0;
    uint16_t voltage;
    uint16_t trigger_counter;
    uint8_t shutdown;
    uint8_t magic1;
} answer_t;
static volatile answer_t answer;
static uint8_t *answer_data = (uint8_t*)&answer;

// Timer
static uint16_t timer_period;
static uint16_t timer_on_time;
static uint16_t timer_trigger_count;
static uint8_t timer_infinite_repeat;
#define timer_on() TCCR1B |= (1<<CS11)
#define timer_off() TCCR1B &= ~(1<<CS11)
void timer_init()
{
    DDRB |= (1<<1); // Set OC1A as output
    TIMSK1 = (1<<TOIE1); // Enable overflow interrupt
    TCCR1A = (1<<COM1A1) | (1<<WGM11);
    TCCR1B = (1<<WGM12) | (1<<WGM13);  // Fast PWM mode, TOP = ICR1, no clock
    ICR1 = timer_period - 1;
    OCR1A = timer_on_time - 1;
    answer.trigger_counter = timer_trigger_count;
}

uint16_t get_voltage()
{
    ADCSRA |= (1<<ADSC);  // Start conversion
    while(ADCSRA & (1<<ADSC));  // Wait for completion
    uint16_t adc_val = ADC;
    ADCSRA |= (1<<ADIF); // Clear interrupt flag

    // convert ADC value to voltage, reference is 1.1V, voltage divider 10/78
    uint16_t voltage = (uint16_t)(adc_val*8.37);
    return voltage;
}

int main()
{
    led_init();
    pi_shtdn_init();
    pi_shtdn_low();
    master_on_init();
    master_on_pu();
    pwr_on_init();
    pwr_on_low();

    // Wait 2 seconds before we actually turn on the power while flashing the LED
    for(int i = 0; i < 20; i++)
    {
        _delay_ms(100);
        led_toggle();
    }
    led_on();
    pwr_on_high();

    // Set up SPI ~SS pin change interrupt
    PORTB |= (1<<2); // Enable pull-up
    PCICR |= (1<<PCIE0);
    PCMSK0 |= (1<<2);

    // Set up SPI slave
    DDRB |= (1<<4); // Set MISO as output
    SPCR = (1<<SPIE) | (1<<SPE);

    // Set up battery monitoring ADC
    ADMUX = (1<<REFS0) | (1<<REFS1) | 7; // 1.1V internal reference, ADC7 source
    ADCSRA = (1<<ADEN) | (1<<ADPS2) | (1<<ADPS1) | (1<<ADPS0);  // Enable, 1/128 prescaler
    get_voltage(); // Dummy read
    _delay_ms(10); // Wait a moment for the bandgap voltage to stabilize

    // Set up trigger timer at OC0A output
    timer_period = 1000;
    timer_on_time = 500;
    timer_trigger_count = 10;
    timer_infinite_repeat = 0;
    timer_init();
    timer_on();  // Do a dummy sequence to prepare the OC1A pin

    answer.shutdown = 0;
    answer.magic0 = 0x31;
    answer.magic1 = 0x41;
    sei();

    uint16_t shutdown_counter = 0;

    while(1)
    {
        // Atomically update the battery voltage and only if we are not selected at the moment
        // This will prevent an update of the voltage while we are currently transmitting it
        uint16_t voltage = get_voltage();
        if(PINB & (1<<2))
        {
            answer.voltage = voltage;
        }
        if(voltage < MIN_VOLTAGE || shutdown_counter > 2000)
        {
            // Request a shutdown of the Pi
            answer.shutdown = 1;
            pi_shtdn_high();
            led_off();
            // Wait 15 seconds before we actually turn on the power while flashing the LED
            for(int i = 0; i < 150; i++)
            {
                _delay_ms(100);
                led_toggle();
            }
            led_off();
            pwr_on_low();
        }
        if(!master_on_val())
            shutdown_counter++;
        else
            shutdown_counter = 0;
        _delay_ms(1);
    }
    return 0;
}

// SPI transfer complete interrupt
ISR(SPI_STC_vect)
{
    // Save data to buffer
    command_buffer_data[spi_byte_cnt] = SPDR;

    // Write next byte and increment byte counter
    // spi_byte_cnt is still 0 after the first byte has been received, so we transmit
    // answer_data[spi_byte_cnt+1]
    if(spi_byte_cnt + 1 < sizeof(command_t))
    {
        SPDR = answer_data[spi_byte_cnt+1];
        spi_byte_cnt++;
    }
}

// PB2 aka ~SS pin toggle interrupt
ISR(PCINT0_vect)
{
    // On selection, write the first byte (magic0)
    if(!(PINB & (1<<2)))
    {
        SPDR = answer_data[0];
        return;
    }
    
    // Reset byte count
    spi_byte_cnt = 0;

    // Interprete the SPI RX buffer
    if(command_buffer.command)
    {
        timer_period = command_buffer.period;
        timer_on_time = command_buffer.on_time;
        timer_trigger_count = command_buffer.trigger_count;
    }
    timer_infinite_repeat = !!(command_buffer.command & COMMAND_INFINITE_REPEAT);
    if(command_buffer.command & COMMAND_START_TRIGGER)
    {
        timer_init();
        timer_on();
    }
    if(command_buffer.command & COMMAND_STOP_TRIGGER)
    {
        timer_off();
    }
}

// Timer 1 overflow interrupt
ISR(TIMER1_OVF_vect)
{
    led_toggle();
    answer.trigger_counter--; // Count the columns
    if(!answer.trigger_counter)
    {
        // Reset counter or turn off trigger signal
        if(timer_infinite_repeat) {
            answer.trigger_counter = timer_trigger_count;
        } else {
            timer_off();
        }
    }
}
