//LeaderArmReader.h
#pragma once
#include <Arduino.h>
#include "LeaderArmTypes.h"

float clampFloat(float value, float low, float high);
int readFilteredAnalog(uint8_t pin, uint8_t samples = 4);
float rawToAngleDeg(int raw, const JointCalibration& cal);