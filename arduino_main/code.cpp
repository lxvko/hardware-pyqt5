// -------------------- БИБЛИОТЕКИ ---------------------
#include <string.h>             // библиотека расширенной работы со строками
#include <LiquidCrystal_I2C.h>  // библтотека дислея
// -------------------- БИБЛИОТЕКИ ---------------------

// ------------------------ НАСТРОЙКИ ----------------------------
#define DRIVER_VERSION 1    // 0 - маркировка драйвера кончается на 4АТ, 1 - на 4Т
#define printByte(args)  write(args);
// ------------------------ НАСТРОЙКИ ----------------------------

// -------- ОПРЕДЕЛЕНИЕ ДИСПЛЕЯ -------------
LiquidCrystal_I2C lcd(0x27, 20, 4);
// -------- ОПРЕДЕЛЕНИЕ ДИСПЛЕЯ -------------

// стартовый логотип
byte logo0[8] = {B11111, B10000, B10000, B11111, B10000, B10000, B11111, B00000};
byte logo1[8] = {B11100, B00010, B00001, B11111, B00001, B00010, B11100, B00000};
byte logo2[8] = {B11111, B00100, B00100, B00100, B00100, B00100, B00100, B00000};
byte logo3[8] = {B10001, B10010, B10100, B11000, B11100, B10010, B10001, B00000};
// значок градуса lcd.write(223);
byte degree[8] = {0b11100,  0b10100,  0b11100,  0b00000,  0b00000,  0b00000,  0b00000,  0b00000};
// правый край полосы загрузки
byte right_empty[8] = {0b11111,  0b00001,  0b00001,  0b00001,  0b00001,  0b00001,  0b00001,  0b11111};
// левый край полосы загрузки
byte left_empty[8] = {0b11111,  0b10000,  0b10000,  0b10000,  0b10000,  0b10000,  0b10000,  0b11111};
// центр полосы загрузки
byte center_empty[8] = {0b11111, 0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b11111};
// блоки для построения графиков
byte row8[8] = {0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111};
byte row7[8] = {0b00000,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111};
byte row6[8] = {0b00000,  0b00000,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111};
byte row5[8] = {0b00000,  0b00000,  0b00000,  0b11111,  0b11111,  0b11111,  0b11111,  0b11111};
byte row4[8] = {0b00000,  0b00000,  0b00000,  0b00000,  0b11111,  0b11111,  0b11111,  0b11111};
byte row3[8] = {0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b11111,  0b11111,  0b11111};
byte row2[8] = {0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b11111,  0b11111};
byte row1[8] = {0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b00000,  0b11111};

char inData[82];       // массив входных значений (СИМВОЛЫ)
int PCdata[20];        // массив численных значений показаний с компьютера
byte index = 0;
String string_convert;
unsigned long timeout;
boolean reDraw_flag = 1, updateDisplay_flag, updateTemp_flag, timeOut_flag = 1;
byte lines[] = {4, 5, 7, 6};
String perc;
boolean timeOutLCDClear = 0, restoreConnectToPC=0;

void setup() {
  Serial.begin(9600);

  // инициализация дисплея
  lcd.init();
  lcd.backlight();
  lcd.clear();              // очистить дисплей
  show_logo();              // показать логотип
  delay(2000);              // на 2 секунды
  lcd.clear();              // очистить дисплей
}

// ------------------------------ ОСНОВНОЙ ЦИКЛ -------------------------------
void loop() {
  parsing();                // парсим строки с компьютера
  updateDisplay();          // обновить показания на дисплее
  timeoutTick();            // проверка таймаута
}
// ------------------------------ ОСНОВНОЙ ЦИКЛ -------------------------------

void parsing() {
  while (Serial.available() > 0) {
    char aChar = Serial.read();
    if (aChar != 'E') {
      inData[index] = aChar;
      index++;
      inData[index] = '\0';
    } else {
      char *p = inData;
      char *str;
      index = 0;
      String value = "";
      while ((str = strtok_r(p, ";", &p)) != NULL) {
        string_convert = str;
        PCdata[index] = string_convert.toInt();
        index++;
      }
      index = 0;
      updateDisplay_flag = 1;
      updateTemp_flag = 1;
    }
    timeout = millis();
    timeOut_flag = 1;
    restoreConnectToPC = 1;
    lcd.backlight();    
   }
}

void updateDisplay() {
  if (updateDisplay_flag) {
    if (reDraw_flag) {                        // если программа запускается впервые
      lcd.clear();
      draw_labels();
      reDraw_flag = 0;
    }
    draw_stats();
    updateDisplay_flag = 0;
  }
  if (timeOutLCDClear) reDraw_flag = 1;
}

void draw_labels() {                          // пишем заголовки
  lcd.createChar(0, degree);
  lcd.createChar(1, left_empty);
  lcd.createChar(2, center_empty);
  lcd.createChar(3, right_empty);
  lcd.createChar(4, row8);
  lcd.setCursor(0, 0);
  lcd.print("CPU:");
  lcd.setCursor(0, 1);
  lcd.print("GPU:");
  lcd.setCursor(0, 2);
  lcd.print("GPUmem:");
  lcd.setCursor(0, 3);
  lcd.print("RAMuse:");
}

void draw_stats() {                           // пишем показания
  timeOutLCDClear = 0;
  lcd.setCursor(4, 0); lcd.print(PCdata[0]); lcd.write(223);
  lcd.setCursor(17, 0); lcd.print(PCdata[4]);
  if (PCdata[4] < 10) perc = "% ";
  else if (PCdata[4] < 100) perc = "%";
  else perc = "";  lcd.print(perc);
  lcd.setCursor(4, 1); lcd.print(PCdata[1]); lcd.write(223);
  lcd.setCursor(17, 1); lcd.print(PCdata[5]);
  if (PCdata[5] < 10) perc = "% ";
  else if (PCdata[5] < 100) perc = "%";
  else perc = "";  lcd.print(perc);
  lcd.setCursor(17, 2); lcd.print(PCdata[7]);
  if (PCdata[7] < 10) perc = "% ";
  else if (PCdata[7] < 100) perc = "%";
  else perc = "";  lcd.print(perc);
  lcd.setCursor(17, 3); lcd.print(PCdata[6]);
  if (PCdata[6] < 10) perc = "% ";
  else if (PCdata[6] < 100) perc = "%";
  else perc = "";  lcd.print(perc);

  for (int i = 0; i < 4; i++) {
    byte line = ceil(PCdata[lines[i]] / 10);
    lcd.setCursor(7, i);
    if (line == 0) lcd.printByte(1)
      else lcd.printByte(4);
    for (int n = 1; n < 9; n++) {
      if (n < line) lcd.printByte(4);
      if (n >= line) lcd.printByte(2);
    }
    if (line == 10) lcd.printByte(4)
      else lcd.printByte(3);
  }
}

void timeoutTick() {
  if ((millis() - timeout > 5000)) lcd.clear();
  while (Serial.available() < 1) {
    if ((millis() - timeout > 5000) && timeOut_flag) {        
      index = 0;
      updateTemp_flag = 1;
      if(restoreConnectToPC) {
       reDraw_flag=1;
       restoreConnectToPC=0;
       if (reDraw_flag) {
       lcd.clear();
       reDraw_flag = 0;}
      } 
      lcd.setCursor(5, 1);
      lcd.print("CONNECTION");
      lcd.setCursor(7, 2);
      lcd.print("FAILED");
      reDraw_flag = 0;
      updateDisplay_flag = 1;
      timeOutLCDClear = 1;
      if (timeOutLCDClear) reDraw_flag = 1;
    }
  }
}

void show_logo() {
  lcd.createChar(0, logo0);
  lcd.createChar(1, logo1);
  lcd.createChar(2, logo2);
  lcd.createChar(3, logo3);
  lcd.setCursor(3, 1);
  lcd.write(0);
  lcd.write(1);
  lcd.setCursor(3, 2);
  lcd.write(2);
  lcd.write(3);
  
  lcd.setCursor(6, 1);
  lcd.print("Don Mikhail");
  lcd.setCursor(6, 2);
  lcd.print("EETK 414-KC");
}