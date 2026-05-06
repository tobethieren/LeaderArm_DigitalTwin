#pragma once
#include <Arduino.h>

// Pin definitions for the potentiometers controlling each joint
const uint8_t PIN_BASIS    = A0;
const uint8_t PIN_MAIN_ARM = A1;
const uint8_t PIN_FORE_ARM = A2;
const uint8_t PIN_WRIST    = A3;

// Timing constants for sending data
const unsigned long SEND_INTERVAL_MS = 20;  // Send data every 20ms