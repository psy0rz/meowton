// meowton - proof of concept for an automatic pet scale

#include "HX711.h"

//moving average smoothing number

//we're trying to measure a moving cat while eating
//assume that it stays on the scale for 20-30 seconds at least, so we take a lot of values to average out movements and noise
#define AVERAGE 100


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





//// test measurements

/*
2016-12-03
5970 midden
5995 rechts voor zeer stabiel. tijdens liggen
t
*/

//////////////////////////////////////////////////////////
HX711 * scale[4];
float average[4];





float factor[4];
void setup() {
    Serial.begin(115200);
    delay(100);
    Serial.println("\n\n\n\n\nstarting...");
    factor[0]=CALIBRATE_FACTOR0;
    factor[1]=CALIBRATE_FACTOR1;
    factor[2]=CALIBRATE_FACTOR2;
    factor[3]=CALIBRATE_FACTOR3;

    //caculate actual factor to get correct weight
    // for (int s=0; s<4; s++)
    // {
    //     factor[s]=factor[s]/CALIBRATED_WEIGHT;
    // }

    //pinout of the 4 weight modules
    // scale[0]=new HX711(0,1);
    // scale[1]=new HX711(2,3);
    // scale[2]=new HX711(4,5);
    // scale[3]=new HX711(6,7);
    // scale[0]=new HX711(1,0);
    scale[0]=new HX711(D6,D7);
    scale[1]=new HX711(D4,D5);
    scale[2]=new HX711(D2,D3);
    scale[3]=new HX711(D0,D1);
    // scale[2]=new HX711(5,4);
    // scale[3]=new HX711(7,6);
    //


    for (int s=0; s<4; s++)
    {
        scale[s]->set_scale();
        Serial.println(s);
        scale[s]->tare(1);	//Reset the scale to 0
    }
}



int tarre_countdown=10;
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
        total=total+(average[s]*CALIBRATED_WEIGHT/factor[s]);
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
    // delay(100);

}
