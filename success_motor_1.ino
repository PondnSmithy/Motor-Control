#include <AccelStepper.h>

// Define the step and direction pins
const int stepPin = 14; 
const int dirPin = 12;
bool stopFlag = true;
bool startFlag = false;

long dist = 0;
int l = 0;
int N = 0;
float speed_f = 0;
// Define the number of steps per revolution
#define STEPS_PER_REV 200*150

// Initialize the AccelStepper object
AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);

void setup() {
  // Set the maximum speed and acceleration of the stepper motor
  Serial.begin(115200);
  stepper.setMaxSpeed(600);
  stepper.setAcceleration(3000);
  ESP.wdtEnable(WDTO_8S);
}

void checkIn(){
  if (Serial.available() > 0) { // if there is data available on serial port
    String input = Serial.readStringUntil('\n'); // read the input string until newline character
    input.trim();
    //Serial.println(input);
    if(input.indexOf('s') != -1){
      stopFlag = true;
      stepper.stop();
      startFlag = false;
      Serial.println("S");
    }
    else{
      int firstCommaIndex = input.indexOf(',');
      int secondCommaIndex = input.indexOf(',', firstCommaIndex + 1);
      speed_f = input.substring(0, firstCommaIndex).toFloat();
      dist = input.substring(firstCommaIndex + 1,secondCommaIndex).toFloat();
      l = input.substring(secondCommaIndex + 1).toInt();
      //แก้ตรงนี้ว่าจะโชว์อะไร
      //Serial.println(speed);
      //Serial.println(dist);
      //Serial.println(l);
      //Serial.println(speed+dist+l);
      //Serial.println("Working");
      stopFlag = false;
      startFlag = true;
    }
  }
}

void Running(float speed,long dist){
  stepper.move(dist);
  stepper.setMaxSpeed(speed_f);
  checkDist();
}

void checkDist(){
  stopFlag = false;
  while(stepper.distanceToGo() != 0){
    checkIn();
    ESP.wdtFeed();
    if(!stopFlag){
      stepper.run();
      //Serial.println("r");
    }
    else{
      //Serial.println("s");
      //Serial.println(stepper.distanceToGo());
      stepper.stop();
      stepper.setCurrentPosition(0);
      startFlag = false;
    }
  }
}

void loop() {
  checkIn();
  if(startFlag){
    if(l!=0){
      int s = dist * l;
      Running(speed_f,s);
      //Serial.println("l!=0");
    startFlag = false;
    }
    if(l==0){
      while(!stopFlag){
        stepper.move(2000);
        stepper.setMaxSpeed(speed_f);
        stepper.run();
        checkIn();
        ESP.wdtFeed();
        //Serial.println("Infinity");
      }
      stepper.setCurrentPosition(0);
    }
    Serial.println(l);
  }
}