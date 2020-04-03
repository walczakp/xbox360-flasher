#define USBSERIAL Serial
#define DBGSERIAL Serial2

#include "XSPI.h"
#include "XNAND.h"

void setup() {
  // put your setup code here, to run once:
  USBSERIAL.begin(1);
  DBGSERIAL.begin(9600);
}

int i = 0;
void loop() {
  // put your main code here, to run repeatedly:
  
  DBGSERIAL.print("Test: ");
  DBGSERIAL.println(i, HEX);
  delay(1000);
  i++;
}
