// meowton - proof of concept for an automatic pet scale

#include "HX711.h"

//moving average smoothing number
//when trying to measure a moving cat, we need a high enough value
#define AVERAGE 20


//auto tarre if measurement didnt change by more than TARRE_MAX_DIFF for TARRE_COUNT measurements
//this is needed because the scale will be running 24/7 and might drift by temperature or other factors
#define TARRE_COUNT 3000
#define TARRE_MAX_DIFF 1

//actual weight you used to calibrate each individual sensor
#define CALIBRATED_WEIGHT 1074 //i use grams

//raw calibration values during measurement of above weight (raw values are always shown in serial output)
#define CALIBRATE_FACTOR0 402600
#define CALIBRATE_FACTOR1 428500
#define CALIBRATE_FACTOR2 443400
#define CALIBRATE_FACTOR3 439700


//pinout
HX711 scale0(3,2); //module 1
HX711 scale1(5,4); //module 2
HX711 scale2(7,6); //module 3
HX711 scale3(9,8); //module 4


//////////////////////////////////////////////////////////
HX711 * scale[4];
float average[4];





float factor[4];
void setup() {
    Serial.begin(115200);
    Serial.println("starting...");

    factor[0]=CALIBRATE_FACTOR0;
    factor[1]=CALIBRATE_FACTOR1;
    factor[2]=CALIBRATE_FACTOR2;
    factor[3]=CALIBRATE_FACTOR3;

    //caculate actual factor to get correct weight
    for (int s=0; s<4; s++)
    {
        factor[s]=factor[s]/CALIBRATED_WEIGHT;
    }


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



int tarre_countdown=AVERAGE*2;
float prev_total=0;

void tarre()
{
    Serial.println("TARRE");
    for (int s=0; s<4; s++)
    {
        scale[s]->set_offset(scale[s]->get_offset()+average[s]);
        average[s]=0;
    }
}

void loop() {


    //read all modules and calculate moving average, print raw data needed to calibrate
    float total=0;
    for (int s=0; s<4; s++)
    {
        long current=scale[s]->get_units();
        average[s]-=average[s]/AVERAGE;
        average[s]+=current/AVERAGE;
        Serial.print(average[s]);
        Serial.print("\t\t");
        total=total+(average[s]/factor[s]);
    }


    //if weight doesnt change much, count down for auto tarre
    if (abs(prev_total-total)<TARRE_MAX_DIFF)
    {
        tarre_countdown--;
        //auto tarre
        if (tarre_countdown==0)
        {
            tarre();
            tarre_countdown=TARRE_COUNT;
        }
    }
    else
    {
        tarre_countdown=TARRE_COUNT;
    }
    prev_total=total;


    Serial.print("t=");
    Serial.print(tarre_countdown);


    Serial.print("\t\tg=");
    Serial.println(total,0);

    if (Serial.available())
    {
        if (Serial.read()=='t')
        {
            tarre();
        }
    }

}
