// meowton - proof of concept for an automatic pet scale

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
#define TARRE_COUNT 3000
#define TARRE_MAX_DIFF 1

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
