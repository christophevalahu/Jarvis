//Code written by David Bretaud
//last modification: 25-Sep-20
//Usage for IQT Sussex research group only
//
//Cerberus:
//Automatic laser beam shutter system
//
#include <Servo.h>
#include <EEPROM.h>
//Objects have to be declared first
String command;
int button_state[]={0,0,0,0};//memory for the button
//if 0 and button pressed, then go to 1 and vice versa
//allows to turn shutter on and off with a single button
int button_pin[]={2,4,8,10};//Arduino connection port
int led_pin[]={6,7,12,13};//Arduino connection port
int servo_pin[]={3,5,9,11};//Arduino connection port
Servo servo1,servo2,servo3,servo4;
Servo servos[]={servo1,servo2,servo3,servo4};
//Setup function is mandatory. Called once at the beginning
void setup() {
  //Serial connection config
  Serial.begin(9600);
  Serial.setTimeout(500);
  //Servo1 config
  for (int i = 0; i <= 3; i++) {
    servos[i].attach(servo_pin[i]);//initialize servos 
    pinMode(led_pin[i], OUTPUT);//configure 
    pinMode(button_pin[i], INPUT_PULLUP);//trick to read button
    //EEPROM is the internal memory
    //Restart the servos in its previous config
    //if it got disconnected
    if (EEPROM.read(i)==0){
      digitalWrite(led_pin[i], LOW);
      servos[i].write(0);//exact angles are arbitrary
    }else if(EEPROM.read(i)==1){
      digitalWrite(led_pin[i], HIGH);
      servos[i].write(90);//just put some carboard in the appropriate position
    }
  }
}
//Main code: run continuously
void loop() {
  //serial communication
  //messages sent:
  //{Cmd}_{Id}
  //{Cmd} can be "off" or "on"
  //{Id} can be {"1","2","3","4","all"}
  if(Serial.available()){//Only works if usb serial connection working
    int len,ind;
    command = Serial.readStringUntil('\n');//Get the message
    len=command.length();
    bool all=(command.substring(len-3,len)=="all");
    if (!all){
      //The command is not sent to all motors
      //So we determine the index sent in the message
      ind=command.substring(len-1,len).toInt()-1;
    }
    if(command.substring(0,3).equals("off")){//Turn off shutters
      if(all){
        for (int i = 0; i <= 3; i++) {
          servos[i].write(0);
          EEPROM.write(i, 0);
          digitalWrite(led_pin[i], LOW);  
          button_state[i] = 0;//button states have to be updated as well 
        }
      }else{
        servos[ind].write(0);
        EEPROM.write(ind, 0);
        digitalWrite(led_pin[ind], LOW);  
        button_state[ind] = 0;
      }
    }else if(command.substring(0,2).equals("on")){
      if(all){
        for (int i = 0; i <= 3; i++) {
          servos[i].write(90);
          EEPROM.write(i, 1);
          digitalWrite(led_pin[i], HIGH);  
          button_state[i] = 1;
        }
      }else{
      servos[ind].write(90);
      EEPROM.write(ind, 1);
      digitalWrite(led_pin[ind], HIGH);  
      button_state[ind] = 1;
      }
    }
  }
  //button reading
  for (int i = 0; i <= 3; i++) {
    if(digitalRead(button_pin[i])==0){
      if(button_state[i]==0){
        servos[i].write(90);
        EEPROM.write(i, 1);
        digitalWrite(led_pin[i], HIGH);  
        button_state[i] = 1;
      }else{
        servos[i].write(0);
        EEPROM.write(i, 0);
        digitalWrite(led_pin[i], LOW);  
        button_state[i] = 0;
      }
    }
  }
  //half a second update rate for not messing with the button
  delay(500);
} 

