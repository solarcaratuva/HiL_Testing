#include <Wire.h>

#define THROTTLE_ADDR 0x2F
#define REGEN_ADDR 0x2E
#define THROTTLE_MARKER 0xFF
#define REGEN_MARKER 0xFE
#define SWAP_COMMAND 0x1FF

// Test Mode: 0 = Throttle only (listen on 0x2F), 1 = Regen only (listen on 0x2E).
// Must match which test is run: test_throttle needs TEST_MODE 0, test_regen needs TEST_MODE 1.
#define TEST_MODE 0

int currentMode = 0; // 0 = Throttle, 1 = Regen

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Arduino Starting...");
  
  // Initialize based on test mode
  if (TEST_MODE == 1) {
    // Start in regen mode
    Wire.begin(REGEN_ADDR);
    currentMode = 1;
    Serial.println("Initialized on REGEN_ADDR (0x2E)");
  } else {
    // Start in throttle mode (default)
    Wire.begin(THROTTLE_ADDR);
    currentMode = 0;
    Serial.println("Initialized on THROTTLE_ADDR (0x2F)");
  }
  
  Wire.onReceive(receiveEvent);
  Serial.println("Ready to receive I2C data");
  Serial.print("TEST_MODE: ");
  Serial.println(TEST_MODE);
}

void loop() {
  delay(100);
}

void receiveEvent(int howMany) {
  if (Wire.available() < 2) return;
  
  // Read 2 bytes (16-bit value)
  int highByte = Wire.read();
  int lowByte = Wire.read();
  int value = ((highByte << 8) | lowByte) & 0x1FF;
  
  // Handle swap command
  if (value == SWAP_COMMAND) {
    //TODO: 
    return;
  }
  // Clamp value to valid range [0, 256]
  if (value > 256) value = 256;
  
  
  // Ensure value stays in valid range after inversion
  if (value > 256) value = 256;
  if (value < 0) value = 0;
  
  // Send based on current mode
  if (currentMode == 0) {
    Serial.write(THROTTLE_MARKER);
    Serial.write(value & 0xFF);        // Low byte
    Serial.write((value >> 8) & 0x01); // Bit 8
  } else {
    Serial.write(REGEN_MARKER);
    Serial.write(value & 0xFF);        // Low byte
    Serial.write((value >> 8) & 0x01); // Bit 8
  }
}
