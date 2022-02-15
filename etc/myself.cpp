#include <LiquidCrystal_I2C.h>
#include "Parser.h"
#include "AsyncStream.h"
#include <GParser.h>
AsyncStream<50> serial(&Serial, ';');
int names[4];
int am_names;
int am;
int perc;

int CPU[2];
String CPUClocks[1];
int GPU[2];
String GPUClocks[2];
int GPUmem[2];
int RAMuse[1];
String RAMmem[2];
String Uptime[1];
String DiskSpace0[1];
String DiskSpace1[1];
String DiskSpace2[1];
String DiskUsage0[2];
String DiskUsage1[2];
String DiskUsage2[2];
byte row8[8] = {0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111};
byte right_empty[8] = {0b11111,  0b00001,  0b00001,  0b00001,  0b00001,  0b00001,  0b00001,  0b11111};
byte left_empty[8] = {0b11111,  0b10000,  0b10000,  0b10000,  0b10000,  0b10000,  0b10000,  0b11111};
byte center_empty[8] = {0b11111, 0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b11111};


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
      Serial.println(serial.buf);
      Serial.println(CPUClocks[0]);
      am_names = data.split();
//      for (byte i = 0; i < am; i++) Serial.println(data[i]);
      switch (data.getInt(0)) {
        case 99:
          am = am_names - 1;
          for (int i = 1; i < am_names; i++) names[i-1] = data.getInt(i);
          break;
        case 98:
          display();
          break;
        case 97:
          lcd.clear();
          lcd.setCursor(7, 1);
          lcd.print("Bye");
          lcd.setCursor(2, 2);
          lcd.print("Have a nice day!");
          break;
        case 95:
          lcd.clear();
          lcd.setCursor(7, 1);
          lcd.print("Hello");
          lcd.setCursor(3, 2);
          lcd.print("Make a choice");
          break;
        case 1:
          for (int i = 0; i < am_names; i++) CPU[i-1] = data.getInt(i);
          break;
        case 2:
          CPUClocks[0] = String(data[1]);
          break;
        case 3:
          for (int i = 0; i < am_names; i++) GPU[i-1] = data.getInt(i);
          break;
        case 4:
          for (int i = 0; i < am_names; i++) GPUClocks[i-1] = String(data[i]);
          break;
        case 5:
          for (int i = 0; i < am_names; i++) GPUmem[i-1] = data.getInt(i);
          break;
        case 6:
          RAMuse[0] = data.getInt(1);
          break;
        case 7:
          for (int i = 0; i < am_names; i++) RAMmem[i-1] = String(data[i]);
          break;
        case 8:
          Uptime[0] = String(data[1]);
          break;
        case 9:
          DiskSpace0[0] = String(data[1]);
          break;
        case 10:
          DiskSpace1[0] = String(data[1]);
          break;
        case 11:
          DiskSpace2[0] = String(data[1]);
          break;
        case 12:
          for (int i = 0; i < am_names; i++) DiskUsage0[i-1] = String(data[i]);
          break;
        case 13:
          for (int i = 0; i < am_names; i++) DiskUsage1[i-1] = String(data[i]);
          break;
        case 14:
          for (int i = 0; i < am_names; i++) DiskUsage2[i-1] = String(data[i]);
          break;
      }
    }
}

void display() {
  lcd.createChar(1, left_empty);
  lcd.createChar(2, right_empty);
  lcd.createChar(3, center_empty);
  lcd.createChar(4, row8);
  int s = 0;
  lcd.clear();
  for (int i = 0; i < (am); i++) {
    lcd.setCursor(0, s);
    switch (names[i]) {
      case 1:
        perc = CPU[1] / 10;
        lcd.print("CPU:");
        lcd.print(CPU[0]);
        lcd.write(223);
        lcd.write(1);
        for (int i = 0; i < 8; i++) lcd.write(3);
        lcd.write(2);
        lcd.setCursor(7, s);
        for (int i = 0; i < perc; i ++) lcd.write(4);
        lcd.setCursor(17, s);
        lcd.print(CPU[1]);
        lcd.print("%");
        lcd.setCursor(0, s);
        s = s + 1;
        break;
      case 2:
        lcd.print("CPU Core ");
        lcd.print(CPUClocks[0]);
        lcd.print(" MHz");
        s = s + 1;
        break;
      case 3:
        perc = GPU[1] / 10;
        lcd.print("GPU:");
        lcd.print(GPU[0]);
        lcd.write(223);
        lcd.write(1);
        for (int i = 0; i < 8; i++) lcd.write(3);
        lcd.write(2);
        lcd.setCursor(7, s);
        for (int i = 0; i < perc; i ++) lcd.write(4);
        lcd.setCursor(17, s);
        lcd.print(GPU[1]);
        lcd.print("%");
        lcd.setCursor(0, s);
        s = s + 1;
        break;
      case 4:
        lcd.print(GPUClocks[0]);
        lcd.print(" MHz");
        lcd.print(' ');
        lcd.print(GPUClocks[1]);
        lcd.print(" MHz");
        s = s + 1;
        break;   
      case 5:
        lcd.print("GPU: ");
        lcd.print(GPUmem[0]);
        lcd.print("MB");
        lcd.print(" - ");
        lcd.print(GPUmem[1]);
        lcd.print("MB");
        s = s + 1;
        break;
      case 6:
        perc = RAMuse[0] / 10;
        lcd.print("RAMmem:");
        lcd.write(1);
        for (int i = 0; i < 8; i++) lcd.write(3);
        lcd.write(2);
        lcd.setCursor(7, s);
        for (int i = 0; i < perc; i ++) lcd.write(4);
        lcd.setCursor(17, s);
        lcd.print(RAMuse[0]);
        lcd.print("%");
        lcd.setCursor(0, s);
        s = s + 1;
        break;
      case 7:
        lcd.print("RAM: ");
        lcd.print(RAMmem[0]);
        lcd.print(" - ");
        lcd.print(RAMmem[1]);
        s = s + 1;
        break;
      case 8:
        lcd.print(Uptime[0]);
        s = s + 1;
        break;      
      case 9:
        lcd.print(DiskSpace0[0]);
        s = s + 1;
        break;
      case 10:
        lcd.print(DiskSpace1[0]);
        s = s + 1;
        break;
      case 11:
        lcd.print(DiskSpace2[0]);
        s = s + 1;
        break;   
      case 12:
        lcd.print(DiskUsage0[0]);
        lcd.setCursor(0, s + 1);
        lcd.print(DiskUsage0[1]);
        lcd.setCursor(0, s);
        s = s + 2;
        break;
      case 13:
        lcd.print(DiskUsage1[0]);
        lcd.setCursor(0, s + 1);
        lcd.print(DiskUsage1[1]);
        lcd.setCursor(0, s);
        s = s + 2;
        break;
      case 14:
        lcd.print(DiskUsage2[0]);
        lcd.setCursor(0, s + 1);
        lcd.print(DiskUsage2[1]);
        lcd.setCursor(0, s);
        s = s + 2;
        break;  
    }
  }
}

void loop() {
  parsing();
}
