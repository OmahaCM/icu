#include <Wire.h>
#define SLAVE_ADDRESS 0x2A
#include <Servo.h>

Servo CamServoX; //Attach the pan servo.
Servo CamServoY; //Attach the tilt servo.

int ServoTimer = 250; // Change to adjust how quickly the servos respond.

int SmallXJump = 3; //Sets the movement amount for small pan jumps
int LargeXJump = 7; //Sets the movement amount for large pan jumps


int SmallYJump = 1; //Sets the movement amount for small pan jumps
int LargeYJump = 2; //Sets the movement amount for large pan jumps

//How close your face is to the edge to trigger a jump.
int SmallYLimit = 40; 
int LargeYLimit = 20;

int SmallXLimit = 40;
int LargeXLimit = 20;

//Set servos to initial position.
int posX = 90; //Servo position.
int posY = 90; //Servo position.

int x1; int y1;int x2; int y2; //Holders for frame dimesions.

// Indexes for getting i2c bytes, then, converting them to integers.
int i = 0;
int varI = 0;

//Sets flag to trigger ServoWrite() from the main loop.
//I tried to put this under 'onRequest' call, but the Raspberry Pi kept giving me errors.
//This flagging was a work around.
int NoServoData = 0;

int dim[12]; //Char array for char[] ---> int conversion.
char d[8]; // Char holder array for byte-->char conversion.

void setup() {
    // initialize i2c as slave
    Wire.begin(SLAVE_ADDRESS);
    Wire.onRequest(sendData); 
    Wire.onReceive(readData);
    Serial.begin(9600);
    
    //Attach servos
    CamServoX.attach(10); //Tilt (Y)
    CamServoY.attach(9); //Pan (X)
    
    //Write initial servo position.
    CamServoX.write(posX); 
    CamServoY.write(posY);
}

void loop() {

//Again, this is the work around.  The flag "NoServoData" is set under the i2c onReceive.
if (NoServoData==1){
  ServoWrite();
}

}

//This is just to show the RPi can be written to.  
//Replace with stuff you want to write to the Pi.
char data[] = "Pasta";  
int index = 0;

// callback for sending data
void sendData() { 
    Wire.write(data[index]);
    ++index;
    if (index >= 5) {
         index = 0;
    }
 }
 
// callback for receiving data.
void readData(int numbytes) {

//Holds the chars
int c;

if (Wire.available() > 0){
  while(Wire.available())    // slave may send less than requested
    c = Wire.read();
}
  //Add each integer to a char array.
  //Skip commas ',' and keep adding the integers until char '\0' is received.
  //Then print out the complete string.
  
  if (c != ','){
    if(c != '\0'){
      d[i] = d[i] + c;  //Appends the characters to an array.
      i++;
    }
  }
  else{
    i=0; //Reset the d char array index.
    if(varI < 7){  //We only want to get integers until we get all four numbers (x1, y1, x2, y2) plus
      dim[varI]=atoi(d); //Convert the d int into ASCII and store it in the dim array.
      d[0]=0;d[1]=0;d[2]=0;d[3]=0;d[4]=0;d[5]=0; //Clear the d array (i2c doesn't like for loops in this function
      varI++; //Increase dim index.
    }
    else{
      //We now have all four numbers, load them into the variables.
      x1=int(dim[4]);
      y1=int(dim[1]);
      x2=int(dim[2]);
      y2=int(dim[3]);

      NoServoData = 1;  //Set the WriteServo() call flag.
      varI=0; //Reset the dim index to prepare for next set of numbers.
      }
   i=0; //Reset some
  }
}

void ServoWrite(){
  int x3 = 160 - x2; // Calculate the distance from the right edge of the screen
  int y3 = 120 - y2; // Calcualte the distance

  
  //For X Axis
  if(x1 < SmallXLimit ){  //Only do small jumps, since not too far away from the edge.
        if(posX>1){ //If the pan servo is at its edge, do nothing.
          for (int i = 0; i < LargeXJump; i++){
            posX++;  // Set the new position
            CamServoX.write(posX); //Make the adjustment.
            delay(ServoTimer); //Delay between servo increments.
          }
      }
  }
  
  if(x3 < SmallXLimit){
      if(posX<180){
          for (int i = 0; i < LargeXJump; i++){
            posX--;
            CamServoX.write(posX);
            Serial.println(posX);            
            delay(ServoTimer);
          }  
      }
  }


  if(x1 < LargeXLimit){
        if(posX>1){
          for (int i = 0; i < SmallXJump; i++){
            posX++;
            CamServoX.write(posX);
            Serial.println(posX);            
            delay(ServoTimer);
          }
      }
  }
  
  if(x3 < LargeXLimit){
      if(posX<180){
        for (int i = 0; i < SmallXJump; i++){
            posX--;
            CamServoX.write(posX);
            Serial.println(posX);            
            delay(ServoTimer);
        }
     }
  }
  

  //For Y Axis
  if(y1 < SmallYLimit ){
        if(posY>1){
          for (int i = 0; i < SmallYJump; i++){
            posY--;
            CamServoY.write(posY);
            Serial.println(posY);
            delay(ServoTimer);
          }
        }
  }
  
  if(y3 < SmallYLimit){
      if(posY<180){
        for (int i = 0; i < SmallYJump; i++){
          posY++;
          CamServoY.write(posY);
          Serial.println(posY);
          delay(ServoTimer);
        }
     }
  }


  if(y1 < LargeYLimit){
        if(posY>1){
          for (int i = 0; i < LargeYJump; i++){
            posY--;
            Serial.println(posY);
            CamServoY.write(posY);
            delay(ServoTimer);
          } 
      }
  }
  
  if(y3 < LargeYLimit){
      if(posY<180){
        for (int i = 0; i < LargeYJump; i++){
          posY++;
          CamServoY.write(posY);
          Serial.println(posY);
          delay(ServoTimer);
        } 
      }
  }

//Reset servo write flag.
NoServoData=0;
}
