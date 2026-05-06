//LeaderArmTypes.h
#pragma once
#include <Arduino.h>

struct JointCalibration {
  int rawMin;
  int rawMax;
  float angleMinDeg;
  float angleMaxDeg;
};