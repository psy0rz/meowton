/*

 Example using the SparkFun HX711 breakout board with a scale

 By: Nathan Seidle

 SparkFun Electronics

 Date: November 19th, 2014

 License: This code is public domain but you buy me a beer if you use this and we meet someday (Beerware license).



 This is the calibration sketch. Use it to determine the calibration_factor that the main example uses. It also

 outputs the zero_factor useful for projects that have a permanent mass on the scale in between power cycles.



 Setup your scale and start the sketch WITHOUT a weight on the scale

 Once readings are displayed place the weight on the scale

 Press +/- or a/z to adjust the calibration_factor until the output readings match the known weight

 Use this calibration_factor on the example sketch



 This example assumes pounds (lbs). If you prefer kilograms, change the Serial.print(" lbs"); line to kg. The

 calibration factor will be significantly different but it will be linearly related to lbs (1 lbs = 0.453592 kg).



 Your calibration factor may be very positive or very negative. It all depends on the setup of your scale system

 and the direction the sensors deflect from zero state

 This example code uses bogde's excellent library: https://github.com/bogde/HX711

 bogde's library is released under a GNU GENERAL PUBLIC LICENSE

 Arduino pin 2 -> HX711 CLK

 3 -> DOUT

 5V -> VCC

 GND -> GND



 Most any pin on the Arduino Uno will be compatible with DOUT/CLK.



 The HX711 board can be powered from 2.7V to 5V so the Arduino 5V power should be fine.



*/



#include "HX711.h"




float calibrated_weight=992;
HX711 scale0(3,2); //module 1
HX711 scale1(5,4); //module 2
HX711 scale2(7,6); //module 3
HX711 scale3(9,8); //module 4

HX711 * scale[4];
float average[4];
float factor[4];





void setup() {
  Serial.begin(115200);
  Serial.println("starting...");

  // factor[0]=66900;
  // factor[1]=139000;
  // factor[2]=110700;
  // factor[3]=116100;
  // factor[0]=280800;
  // factor[1]=334300;
  // factor[2]=311800;
  // factor[3]=322550;
  factor[0]=402600;
  factor[1]=428500;
  factor[2]=443400;
  factor[3]=439700;

  float factor_total=0;
  for (int s=0; s<4; s++)
  {
      factor_total+=factor[s];
  }

  for (int s=0; s<4; s++)
  {
    //   factor[s]= factor[s]/  ( calibrated_weight * (factor[s]/factor_total)) ;
    factor[s]=factor[s]/calibrated_weight;


  }


  // factor[0]=18500 ;
  // factor[1]=19800;
  // factor[2]=20500;
  // factor[3]=20300;

  scale[0]=&scale0;
  scale[1]=&scale1;
  scale[2]=&scale2;
  scale[3]=&scale3;



  for (int s=0; s<4; s++)
  {
      scale[s]->set_scale();
      Serial.println(s);
      scale[s]->tare(1);	//Reset the scale to 0
  }
}


#define AVERAGE 5
#define TARRE_COUNT 600
#define TARRE_MAX_DIFF 1

int tarre_countdown=TARRE_COUNT;
float prev_total=0;
void loop() {


  // Serial.print("Raw : ");

  // long total=0;

  for (int s=0; s<4; s++)
  {
      long current=scale[s]->get_units();
      average[s]-=average[s]/AVERAGE;
      average[s]+=current/AVERAGE;
      Serial.print(average[s]);
      Serial.print("\t\t");
    //   total=total+average[s];
  }

  // Serial.println();
  float total=0;
  for (int s=0; s<4; s++)
  {
    //   Serial.print(average[s]/factor[s],3);
    //   Serial.print("\t\t");
      total=total+(average[s]/factor[s]);
    //   total=total+average[s];
  }


  if (abs(prev_total-total)<TARRE_MAX_DIFF)
    tarre_countdown--;
  else
    tarre_countdown=TARRE_COUNT;
  prev_total=total;

  if (tarre_countdown==0)
  {
      Serial.println("TARRE");
      for (int s=0; s<4; s++)
      {
          scale[s]->set_offset(scale[s]->get_offset()+average[s]);
      }
      tarre_countdown=TARRE_COUNT;
  }

  Serial.print("t=");
  Serial.print(tarre_countdown);


  Serial.print("\t\tg=");
  Serial.println(total,0);


}
