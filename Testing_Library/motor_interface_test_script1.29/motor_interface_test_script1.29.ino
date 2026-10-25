// Board: Raspberry Pi Pico (arduino-pico). Both motor addresses, one session.
// SDA/SCL are the Pico pins wired to MotorBoard PA8 and PA9.
// ponytail: core 1 busy-polls. Hardware I2C matches one address, so this
// bit-bangs. Fine for 100 kHz, 2-byte writes. Move to a PIO slave if the
// bus leaves standard mode.

#include "hardware/gpio.h"
#include "hardware/structs/sio.h"
#include "hardware/sync.h"
#include "pico/util/queue.h"

static const uint SDA_PIN = 0;
static const uint SCL_PIN = 1;

static const uint8_t THROTTLE_ADDR = 0x2F;
static const uint8_t REGEN_ADDR = 0x2E;
static const uint8_t THROTTLE_MARKER = 0xFF;
static const uint8_t REGEN_MARKER = 0xFE;

static queue_t reports;
static volatile bool reports_ready = false;

static inline bool pin_high(uint pin) {
  return sio_hw->gpio_in & (1u << pin);
}

static inline void drive_low(uint pin) {
  sio_hw->gpio_clr = 1u << pin;
  sio_hw->gpio_oe_set = 1u << pin;
}

static inline void release(uint pin) {
  sio_hw->gpio_oe_clr = 1u << pin;
}

static void init_pin(uint pin) {
  gpio_init(pin);
  gpio_set_function(pin, GPIO_FUNC_SIO);
  gpio_pull_up(pin);
  gpio_put(pin, 0);
  release(pin);
}

static void wait_start() {
  for (;;) {
    while (!pin_high(SDA_PIN) || !pin_high(SCL_PIN)) {
    }
    while (pin_high(SCL_PIN)) {
      if (!pin_high(SDA_PIN)) return;
    }
  }
}

static uint8_t read_byte() {
  uint8_t byte = 0;
  for (int bit = 0; bit < 8; bit++) {
    while (pin_high(SCL_PIN)) {
    }
    while (!pin_high(SCL_PIN)) {
    }
    byte = (uint8_t)((byte << 1) | (pin_high(SDA_PIN) ? 1 : 0));
  }
  while (pin_high(SCL_PIN)) {
  }
  return byte;
}

static void ack() {
  drive_low(SDA_PIN);
  while (!pin_high(SCL_PIN)) {
  }
  while (pin_high(SCL_PIN)) {
  }
  release(SDA_PIN);
}

static void nack() {
  release(SDA_PIN);
  while (!pin_high(SCL_PIN)) {
  }
  while (pin_high(SCL_PIN)) {
  }
}

static void wait_stop() {
  while (!pin_high(SCL_PIN) || !pin_high(SDA_PIN)) {
  }
}

static void listen() {
  for (;;) {
    wait_start();
    uint8_t addr = read_byte();
    uint8_t marker;
    if (addr == (uint8_t)(THROTTLE_ADDR << 1)) marker = THROTTLE_MARKER;
    else if (addr == (uint8_t)(REGEN_ADDR << 1)) marker = REGEN_MARKER;
    else {
      nack();
      wait_stop();
      continue;
    }
    ack();
    uint8_t hi = read_byte();
    ack();
    uint8_t lo = read_byte();
    ack();
    wait_stop();

    uint16_t value = (uint16_t)(((hi << 8) | lo) & 0x1FF);
    if (value > 256) value = 256;
    uint32_t item = ((uint32_t)marker << 16) | value;
    queue_try_add(&reports, &item);
  }
}

void setup() {
  queue_init(&reports, sizeof(uint32_t), 8);
  reports_ready = true;
  Serial.begin(9600);
}

void setup1() {
  while (!reports_ready) {
  }
  init_pin(SDA_PIN);
  init_pin(SCL_PIN);
  save_and_disable_interrupts();
  listen();
}

void loop() {
  uint32_t item;
  if (!queue_try_remove(&reports, &item)) return;
  uint16_t value = (uint16_t)(item & 0x1FF);
  uint8_t frame[3] = {
      (uint8_t)(item >> 16),
      (uint8_t)(value & 0xFF),
      (uint8_t)((value >> 8) & 0x01),
  };
  Serial.write(frame, 3);
}
