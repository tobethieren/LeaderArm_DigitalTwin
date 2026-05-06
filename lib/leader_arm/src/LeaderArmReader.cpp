//LeaderArmReader.cpp
#include <Arduino.h>
#include "LeaderArmReader.h"

// Clamp a value between minimum and maximum bounds
float clampFloat(float value, float low, float high) {
  if (value < low) return low;
  if (value > high) return high;
  return value;
}

// Read analog pin multiple times and return averaged value (noise reduction)
int readFilteredAnalog(uint8_t pin, uint8_t samples) {
  long sum = 0;

  for (uint8_t i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delayMicroseconds(500);  // Small delay between samples
  }

  return (int)(sum / samples);  // Return average
}

// Convert raw ADC value to angle in degrees using calibration data
float rawToAngleDeg(int raw, const JointCalibration& cal) {
  // Avoid division by zero
  if (cal.rawMax == cal.rawMin) {
    return cal.angleMinDeg;
  }

  // Normalize raw value to 0-1 range
  float t = (float)(raw - cal.rawMin) / (float)(cal.rawMax - cal.rawMin);
  t = clampFloat(t, 0.0f, 1.0f);  // Ensure value is within 0-1

  // Map normalized value to angle range
  return cal.angleMinDeg + t * (cal.angleMaxDeg - cal.angleMinDeg);
}