//LeaderArmSettings.h
#pragma once
#include <Arduino.h>
#include "LeaderArmTypes.h"

struct StoredSettings {
  uint16_t magic;
  uint8_t version;
  uint8_t isCalibrated;

  JointCalibration basisCal;
  JointCalibration mainArmCal;
  JointCalibration foreArmCal;
  JointCalibration wristCal;
};

void setDefaultSettings(StoredSettings& settings);
bool loadSettingsFromEEPROM(StoredSettings& settings);
void saveSettingsToEEPROM(const StoredSettings& settings);
void clearSettingsInEEPROM();