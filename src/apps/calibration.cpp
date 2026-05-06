#include <Arduino.h>
#include "LeaderArmTypes.h"
#include "LeaderArmConfig.h"
#include "LeaderArmSettings.h"

struct AxisConfig {
  const char* jointName;
  uint8_t pin;
  const char* firstPrompt;
  const char* secondPrompt;
  float firstAngleDeg;
  float secondAngleDeg;
};

// ======================================================
// HIER PAS JE ZELF JE HOEKEN AAN
// PIN_BASIS    = basis
// PIN_MAIN_ARM = main arm
// PIN_FORE_ARM = voorarm
// PIN_WRIST    = pols
// ======================================================
AxisConfig axes[] = {
  {
    "basis",
    PIN_BASIS,
    "Draai de BASIS volledig linksom en druk Enter...",
    "Draai de BASIS volledig rechtsom en druk Enter...",
    -180.0f,   // hoek bij volledig links
     180.0f    // hoek bij volledig rechts
  },
  {
    "mainArm",
    PIN_MAIN_ARM,
    "Draai de MAIN ARM volledig naar achter en druk Enter...",
    "Draai de MAIN ARM volledig naar voor en druk Enter...",
    -90.0f,     // hoek bij volledig naar achter
    90.0f    // hoek bij volledig naar voor
  },
  {
    "foreArm",
    PIN_FORE_ARM,
    "Draai de VOORARM volledig naar achter en druk Enter...",
    "Draai de VOORARM volledig naar voor en druk Enter...",
    -90.0f,     // hoek bij volledig naar achter
    90.0f    // hoek bij volledig naar voor
  },
  {
    "wrist",
    PIN_WRIST,
    "Draai de POLS volledig omlaag en druk Enter...",
    "Draai de POLS volledig omhoog en druk Enter...",
    -90.0f,   // hoek bij volledig omlaag
     90.0f    // hoek bij volledig omhoog
  }
};
// ======================================================

const uint8_t AXIS_COUNT = sizeof(axes) / sizeof(axes[0]);
JointCalibration cal[AXIS_COUNT];

int readStableAnalog(uint8_t pin, uint8_t samples = 20) {
  long sum = 0;

  for (uint8_t i = 0; i < samples; i++) {
    sum += analogRead(pin);
    delay(5);
  }

  return (int)(sum / samples);
}

void flushSerialInput() {
  while (Serial.available() > 0) {
    Serial.read();
  }
}

void waitForEnter() {
  while (true) {
    while (Serial.available() > 0) {
      char c = Serial.read();

      if (c == '\n' || c == '\r') {
        delay(50);
        flushSerialInput();
        return;
      }
    }
  }
}

void calibrateAxis(int index) {
  AxisConfig& a = axes[index];

  Serial.println();
  Serial.print("=== Kalibratie ");
  Serial.print(a.jointName);
  Serial.println(" ===");

  Serial.println(a.firstPrompt);
  waitForEnter();
  int raw1 = readStableAnalog(a.pin);
  Serial.print("Gemeten raw = ");
  Serial.println(raw1);

  Serial.println();

  Serial.println(a.secondPrompt);
  waitForEnter();
  int raw2 = readStableAnalog(a.pin);
  Serial.print("Gemeten raw = ");
  Serial.println(raw2);

  // Zorg dat rawMin < rawMax blijft,
  // en dat de bijbehorende hoeken correct meegaan.
  if (raw1 <= raw2) {
    cal[index].rawMin = raw1;
    cal[index].rawMax = raw2;
    cal[index].angleMinDeg = a.firstAngleDeg;
    cal[index].angleMaxDeg = a.secondAngleDeg;
  } else {
    cal[index].rawMin = raw2;
    cal[index].rawMax = raw1;
    cal[index].angleMinDeg = a.secondAngleDeg;
    cal[index].angleMaxDeg = a.firstAngleDeg;
  }

  Serial.println("Opgeslagen.");
}

void saveCalibrationToEEPROM() {
  StoredSettings settings;
  setDefaultSettings(settings);

  settings.isCalibrated = 1;
  settings.basisCal = cal[0];
  settings.mainArmCal = cal[1];
  settings.foreArmCal = cal[2];
  settings.wristCal = cal[3];

  saveSettingsToEEPROM(settings);
}

void printResults() {
  Serial.println();
  Serial.println("===== RESULTATEN =====");
  Serial.println();

  Serial.print("basisCal   = {");
  Serial.print(cal[0].rawMin);
  Serial.print(", ");
  Serial.print(cal[0].rawMax);
  Serial.print(", ");
  Serial.print(cal[0].angleMinDeg, 2);
  Serial.print("f, ");
  Serial.print(cal[0].angleMaxDeg, 2);
  Serial.println("f}");

  Serial.print("mainArmCal = {");
  Serial.print(cal[1].rawMin);
  Serial.print(", ");
  Serial.print(cal[1].rawMax);
  Serial.print(", ");
  Serial.print(cal[1].angleMinDeg, 2);
  Serial.print("f, ");
  Serial.print(cal[1].angleMaxDeg, 2);
  Serial.println("f}");

  Serial.print("foreArmCal = {");
  Serial.print(cal[2].rawMin);
  Serial.print(", ");
  Serial.print(cal[2].rawMax);
  Serial.print(", ");
  Serial.print(cal[2].angleMinDeg, 2);
  Serial.print("f, ");
  Serial.print(cal[2].angleMaxDeg, 2);
  Serial.println("f}");

  Serial.print("wristCal   = {");
  Serial.print(cal[3].rawMin);
  Serial.print(", ");
  Serial.print(cal[3].rawMax);
  Serial.print(", ");
  Serial.print(cal[3].angleMinDeg, 2);
  Serial.print("f, ");
  Serial.print(cal[3].angleMaxDeg, 2);
  Serial.println("f}");

  Serial.println();
  Serial.println("Kalibratie opgeslagen in EEPROM.");
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("INTERACTIEVE KALIBRATIE LEADER ARM");
  Serial.println("Open Serial Monitor op 115200 baud.");
  Serial.println("Per joint: draai naar eerste limiet -> Enter, dan naar tweede limiet -> Enter.");
  Serial.println();

  for (uint8_t i = 0; i < AXIS_COUNT; i++) {
    calibrateAxis(i);
  }

  saveCalibrationToEEPROM();
  printResults();
}

void loop() {
}