#include "XSPI.h"
#include "XNAND.h"
#include "defs.h"

#define USBSERIAL Serial
#define DBGSERIAL Serial2

#define dbg(MSG) DBGSERIAL.print(F(MSG))
#define dbgf(MSG, ...) DBGSERIAL.printf(F(MSG), __VA_ARGS__) 

uint32_t read_param_le(void);
void StartFlashRead(uint32_t, uint32_t);
void StartFlashWrite(uint32_t, uint32_t);
void FlashInit(void);
void FlashDeinit(void);
void FlashStatus(void);

uint16_t STATUS = 0;
uint8_t PAGE_BUFFER[0x210] = {};

void setup() {
  // put your setup code here, to run once:
  USBSERIAL.begin(115200);
  DBGSERIAL.begin(9600);

  dbg("Init SPI\n");
  XSPI_Init();
}

void loop() {
  if (USBSERIAL.available()) {
    int16_t command = USBSERIAL.read();  // serial.read is 0-255 or -1 :(
    
    if (command > 0) {
      uint32_t paramA = read_param_le();
      uint32_t paramB = read_param_le();
      switch(command)
      {
        case REQ_DATAREAD: StartFlashRead(paramA << 5, paramB); break;
        case REQ_DATAWRITE: StartFlashWrite(paramA << 5, paramB); break;
        case REQ_DATAINIT: FlashInit(); break;
        case REQ_DATADEINIT: FlashDeinit(); break;
        case REQ_DATASTATUS: FlashStatus(); break;
    //    case REQ_DATAERASE: FlashErase(paramA << 5); break;
    //    case REQ_POWERUP: PowerUp(); break;
    //    case REQ_SHUTDOWN: Shutdown(); break;
    //    case REQ_UPDATE: Update(); break;
      }
    }
  }
}

uint32_t read_param_le() {
  uint32_t buffer = 0;
  int16_t read = -1;
  for(int i = 0; i < 4; ) {
      if (USBSERIAL.available()) {
        read = USBSERIAL.read();
        buffer = (buffer >> 8) | (read << 24);
        i++;
      }
  }
  return buffer;
}


void StartFlashRead(uint32_t startPage, uint32_t len) {
    uint8_t* buff_ptr = PAGE_BUFFER;
    STATUS = 0;
    uint32_t wordsLeft = 0;
    uint32_t nextPage = startPage;

    len /= 4;
    while(len) {
        uint8_t readNow;
        
        if(!wordsLeft)
        {
            STATUS = XNAND_StartRead(nextPage);
            nextPage++;
            wordsLeft = 0x84;
            buff_ptr = PAGE_BUFFER;
        }
        
        readNow = (len < wordsLeft) ? len : wordsLeft;
        XNAND_ReadFillBuffer(buff_ptr, readNow);
        
        buff_ptr += (readNow*4);
        wordsLeft -= readNow;
        len -= readNow;

        if(!wordsLeft) {
          USBSERIAL.write(PAGE_BUFFER, 0x210);
        }
    }
}

void StartFlashRead(uint32_t startPage, uint32_t len) {
    STATUS = XNAND_Erase(startPage);
    XNAND_StartWrite();

    uint32_t wordsLeft = 0;
    uint32_t nextPage = startPage;
    len /= 4;
    while(len)
    {
        uint8_t writeNow;
        
        if(!wordsLeft)
        {
            nextBlock++;
            wordsLeft = 0x84;
        }
        
        writeNow = (len < wordsLeft) ? len : wordsLeft;
        XNAND_WriteProcess(buffer, writeNow);
        
        buffer += (writeNow*4);
        wordsLeft -= writeNow;
        len -= writeNow;
        
        //execute write if buffer in NAND controller is filled
        if(!wordsLeft)
        {
            STATUS = XNAND_WriteExecute(nextBlock-1);
            XNAND_StartWrite();
        }
    }
}

void FlashInit(void) {
  dbg("Entering flashmode\n");
  XSPI_EnterFlashmode();

  dbg("Reading flashconfig\n");
  uint8_t FlashConfig[4];
  XSPI_Read(0, FlashConfig);  //2 times?
  XSPI_Read(0, FlashConfig);

  USBSERIAL.write(FlashConfig, 4);
}

void FlashDeinit() {
  dbg("Leaving flashmode\n");
  XSPI_LeaveFlashmode();
}

void FlashStatus() {
  uint8_t FlashStatus[2] = {(uint8_t)(STATUS & 0xFF), (uint8_t)(STATUS >> 8)};
  USBSERIAL.write(FlashStatus, 2);
}
