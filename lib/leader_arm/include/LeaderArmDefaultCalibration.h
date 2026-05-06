// LeaderArmDefaultCalibration.h
#pragma once
#include "LeaderArmTypes.h"

// Fallback/default calibration values
// These are used when no valid calibration is found in EEPROM.
static const JointCalibration basisCal   = {0, 1023, -150.0f, 150.0f};   // Base joint
static const JointCalibration mainArmCal = {0, 1023,    -90.0f, 90.0f};   // Main arm
static const JointCalibration foreArmCal = {0, 1023,    -90.0f, 90.0f};   // Forearm
static const JointCalibration wristCal   = {0, 1023,  -90.0f,  90.0f};   // Wrist joint