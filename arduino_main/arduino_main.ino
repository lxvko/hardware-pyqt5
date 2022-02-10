#include <LiquidCrystal_I2C.h>
#include "Parser.h"
#include "AsyncStream.h"
#include <GParser.h>
AsyncStream<50> serial(&Serial, ';');
int names[4];
int am;

int CPU[2];
float CPUClocks[1];
int GPU[2];
float GPUClocks[2];
int GPUmem[2];
int RAMuse[1];
float RAMmem[2];
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
    if (serial.available()) {
      GParser data(serial.buf, ',');
      am = data.split();
//      for (byte i = 0; i < am; i++) Serial.println(names[i]);
      switch (data.getInt(0)) {
        case 99:
          for (int i = 0; i < am; i++) names[i-1] = data.getInt(i);
          break;
        case 1:
          for (int i = 0; i < am; i++) CPU[i-1] = data.getInt(i);
          break;
        case 2:
          CPUClocks[0] = data.getFloat(1);
          break;
        case 3:
          for (int i = 0; i < am; i++) GPU[i-1] = data.getInt(i);
          break;
        case 4:
          for (int i = 0; i < am; i++) GPUClocks[i-1] = data.getFloat(i);
          break;
        case 5:
          for (int i = 0; i < am; i++) GPUmem[i-1] = data.getInt(i);
          break;
        case 6:
          RAMuse[0] = data.getInt(1);
          break;
        case 7:
          for (int i = 0; i < am; i++) RAMmem[i-1] = data.getFloat(i);
          break;
        case 8:
          Uptime[0] = data.getInt(1);
          break;
      }
    }
}

void display() {
  lcd.clear();
  for (int i = 0; i < (am - 1); i++){
    lcd.setCursor(0, i);
    lcd.print(names[i]);
    lcd.setCursor(2, i);
    switch (names[i]) {
      case 1:
      lcd.print(CPU[0]);
      lcd.print(' ');
      lcd.print(CPU[1]);
      break;
      case 2:
      lcd.print(CPUClocks[0]);
      break;
      case 3:
      lcd.print(GPU[i]);
      break;
      case 4:
      lcd.print(GPUClocks[i]);
      break;   
      case 5:
      lcd.print(GPUmem[i]);
      break;
      case 6:
      lcd.print(RAMuse[0]);
      break;
      case 7:
      lcd.print(RAMmem[i]);
      break;
      case 8:
      lcd.print(Uptime[0]);
      break;           
    }
  }
}

void loop() {
  parsing();
  delay(300);
  display();
}


       // lcd.clear();
       // lcd.home();
       // lcd.print(data[1]);
       // lcd.setCursor(0,1);
