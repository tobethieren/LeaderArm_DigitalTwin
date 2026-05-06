//LeaderArmSettings.cpp
#include <Arduino.h>
#include <EEPROM.h>
#include "LeaderArmSettings.h"
#include "LeaderArmDefaultCalibration.h"

namespace {
  const uint16_t SETTINGS_MAGIC = 0x4C41;  // "LA" = Leader Arm
  const uint8_t SETTINGS_VERSION = 1;
  const int EEPROM_ADDRESS = 0;
}

void setDefaultSettings(StoredSettings& settings) {
  settings.magic = SETTINGS_MAGIC;
  settings.version = SETTINGS_VERSION;
  settings.isCalibrated = 0;

  // Fallback/default calibration values from header
  settings.basisCal = basisCal;
  settings.mainArmCal = mainArmCal;
  settings.foreArmCal = foreArmCal;
  settings.wristCal = wristCal;
}

bool loadSettingsFromEEPROM(StoredSettings& settings) {
  EEPROM.get(EEPROM_ADDRESS, settings);

  if (settings.magic != SETTINGS_MAGIC || settings.version != SETTINGS_VERSION) {
    setDefaultSettings(settings);
    return false;
  }

  return settings.isCalibrated != 0;
}

void saveSettingsToEEPROM(const StoredSettings& settings) {
  EEPROM.put(EEPROM_ADDRESS, settings);
}

void clearSettingsInEEPROM() {
  StoredSettings settings;
  setDefaultSettings(settings);
  settings.isCalibrated = 0;
  EEPROM.put(EEPROM_ADDRESS, settings);
}