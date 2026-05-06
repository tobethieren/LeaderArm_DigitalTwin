#include <Arduino.h>
#include "LeaderArmConfig.h"
#include "LeaderArmReader.h"
#include "LeaderArmSettings.h"

unsigned long lastSend = 0;
StoredSettings settings;

void setup() {
  Serial.begin(115200);  // Initialize serial communication at 115200 baud

  bool hasValidCalibration = loadSettingsFromEEPROM(settings);

  if (hasValidCalibration) {
    Serial.println("EEPROM_STATUS:CALIBRATED");
    Serial.println("Valid calibration loaded from EEPROM.");
  } else {
    Serial.println("EEPROM_STATUS:DEFAULT");
    Serial.println("No valid EEPROM calibration found. Using fallback calibration.");
  }
}

void loop() {
  // Send data at fixed intervals (20ms)
  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis();

    // Read and filter analog values from all joints
    int rawBasis = readFilteredAnalog(PIN_BASIS);
    int rawMain = readFilteredAnalog(PIN_MAIN_ARM);
    int rawFore = readFilteredAnalog(PIN_FORE_ARM);
    int rawWrist = readFilteredAnalog(PIN_WRIST);

    // Convert raw values to angles using loaded calibration
    float basisDeg = rawToAngleDeg(rawBasis, settings.basisCal);
    float mainDeg = rawToAngleDeg(rawMain, settings.mainArmCal);
    float foreDeg = rawToAngleDeg(rawFore, settings.foreArmCal);
    float wristDeg = rawToAngleDeg(rawWrist, settings.wristCal);

    // Send angles as CSV format: basis,main,fore,wrist
    Serial.print(basisDeg, 2);
    Serial.print(",");
    Serial.print(mainDeg, 2);
    Serial.print(",");
    Serial.print(foreDeg, 2);
    Serial.print(",");
    Serial.println(wristDeg, 2);
  }
}