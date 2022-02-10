#include <LiquidCrystal_I2C.h>
#include "Parser.h"
#include "AsyncStream.h"
#include <GParser.h>
AsyncStream<50> serial(&Serial, ';');
int names[10];

int CPU[2];
int CPUClocks[1];
int GPU[2];
int GPUClocks[2];
int GPUmem[2];
int RAMuse[1];
int RAMmem[2];
int Uptime[1];

LiquidCrystal_I2C lcd(0x27, 20, 4);

void setup() {
  Serial.begin(115200);
  pinMode(13, 0);
  lcd.init();
  lcd.backlight();
}


// 1 - CPU        -   2
// 2 - CPUClocks  -   1
// 3 - GPU        -   2
// 4 - GPUClocks  -   2
// 5 - GPUmem     -   2
// 6 - RAMuse     -   1
// 7 - RAMmem     -   2
// 8 - Uptime     -   1

void parsing() {
//  if (serial.available()) {
//    Parser data(serial.buf, ',');
//    int ints[20];
//    data.parseInts(ints);
//    int am = data.split();

    if (serial.available()) {
      GParser data(serial.buf, ',');
      int am = data.split();
      for (byte i = 0; i < am; i++) Serial.println(data[i]);

    switch (ints[0]) {
      case 99:
        for (int i = 0; i < am; i++) {
          names[i-1] = ints[i];
        }
        break;
      case 1:
        for (int i = 0; i < am; i++) {
          CPU[i-1] = ints[i];
        }
        Serial.println(CPU[0]);
        Serial.println(CPU[1]);
        break;
      case 2:
        CPUClocks[0] = ints[1];
        Serial.println(CPUClocks[0]);
        break;
      case 3:
        for (int i = 0; i < am; i++) {
          GPU[i-1] = ints[i];
        }
        Serial.println(GPU[0]);
        Serial.println(GPU[1]);
        break;
      case 4:
        for (int i = 0; i < am; i++) {
          GPUClocks[i-1] = ints[i];
        }
        Serial.println(GPUClocks[0]);
        Serial.println(GPUClocks[1]);
        break;
      case 5:
        for (int i = 0; i < am; i++) {
          GPUmem[i-1] = ints[i];
        }
        Serial.println(GPUmem[0]);
        Serial.println(GPUmem[1]);
        break;
      case 6:
        RAMuse[0] = ints[1];
        Serial.println(RAMuse[0]);
        break;
      case 7:
        for (int i = 0; i < am; i++) {
          RAMmem[i-1] = ints[i];
        }
        Serial.println(RAMmem[0]);
        Serial.println(RAMmem[1]);
        break;
      case 8:
        Uptime[0] = ints[1];
        Serial.println(Uptime[0]);
        break;
    }
  }
}

void loop() {
  parsing();
}


       // lcd.clear();
       // lcd.home();
       // lcd.print(data[1]);
       // lcd.setCursor(0,1);