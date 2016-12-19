// meowton - proof of concept for an automatic pet scale

#include "HX711.h"
#include <ESP8266mDNS.h>
#include <ESP8266WiFi.h>
#include "FS.h"
#include <ArduinoOTA.h>
// #include <String>
#include <ESP8266HTTPClient.h>

//moving average smoothing number

//we're trying to measure a moving cat while eating
//assume that it stays on the scale for 20-30 seconds at least, so we take a lot of values to average out movements and noise
// #define AVERAGE 100

//send all raw measurement data to this server in json format
//(for analyses or debugging and tuning)
#define RAW_URL "http://192.168.13.22:8080/raw"
// #define RAW_URL "http://192.168.13.236:8080/raw"
//max buffer size: ESP8266HTTPClient has small buffer sizes
#define RAW_SIZE 2000

// //auto tarre if measurement didnt change by more than TARRE_MAX_DIFF for TARRE_COUNT measurements
// //this is needed because the scale will be running 24/7 and might drift by temperature or other factors
// #define TARRE_COUNT 3000
// #define TARRE_MAX_DIFF 1
//
// //actual weight you used to calibrate each individual sensor
// #define CALIBRATED_WEIGHT 1074 //i use grams
//
// //raw calibration values during measurement of above weight (raw values are always shown in serial output)
// #define CALIBRATE_FACTOR0 402600
// #define CALIBRATE_FACTOR1 428500
// #define CALIBRATE_FACTOR2 443400
// #define CALIBRATE_FACTOR3 439700





//// test measurements

/*
2016-12-03
5970 midden
5995 rechts voor zeer stabiel. tijdens liggen
t
*/


void OTA_config()
{
    ArduinoOTA.onStart([]() {
        Serial.println("OTA: Start");
        SPIFFS.end(); //important
    });
    ArduinoOTA.onEnd([]() {
        Serial.println("\nOTA: End");
        //"dangerous": if you reset during flash you have to reflash via serial
        //so dont touch device until restart is complete
        Serial.println("\nOTA: DO NOT RESET OR POWER OFF UNTIL BOOT+FLASH IS COMPLETE.");
        delay(100);
        ESP.reset();
    });
    ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {

        Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
    });
    ArduinoOTA.onError([](ota_error_t error) {
        Serial.printf("Error[%u]: ", error);
        if (error == OTA_AUTH_ERROR) Serial.println("OTA: Auth Failed");
        else if (error == OTA_BEGIN_ERROR) Serial.println("OTA: Begin Failed");
        else if (error == OTA_CONNECT_ERROR) Serial.println("OTA: Connect Failed");
        else if (error == OTA_RECEIVE_ERROR) Serial.println("OTA: Receive Failed");
        else if (error == OTA_END_ERROR) Serial.println("OTA: End Failed");
    });
    ArduinoOTA.begin();
}

void wifi_config()
{
    File wifi_config_fh = SPIFFS.open("/wifi.txt", "r");
    if (!wifi_config_fh) {
        Serial.println("cannot load wifi config.");
    }
    else
    {
        String ssid=wifi_config_fh.readStringUntil('\n');
        String password=wifi_config_fh.readStringUntil('\n');

        Serial.print("Wifi connecting to: ");
        Serial.println(ssid.c_str());
        WiFi.begin(ssid.c_str(), password.c_str());
    }
}

int last_wifi_status=-1;
void wifi_status()
{
    if (WiFi.status() != last_wifi_status)
    {
        last_wifi_status=WiFi.status();
        if (last_wifi_status==WL_CONNECTED)
        {
            Serial.print("Wifi connected IP address: ");
            Serial.print(WiFi.localIP());
            Serial.print(", strength: ");
            Serial.println(WiFi.RSSI());
        }
        else
        {
            Serial.print("Wifi disconnected, status:");
            Serial.println(last_wifi_status);
        }

    }
}



//////////////////////////////////////////////////////////
HX711 * scale[4];
// float average[4];
// float factor[4];
void setup() {
    //generic stuff that needs to be in a library some day?
    Serial.begin(115200);
    delay(100);
    Serial.println("\n\n\n\n\nmeowton starting...");

    if (!SPIFFS.begin())
        Serial.println("SPIFFS: error while mounting");

    wifi_config();
    OTA_config();

    //actual meowton stuff

    // factor[0]=CALIBRATE_FACTOR0;
    // factor[1]=CALIBRATE_FACTOR1;
    // factor[2]=CALIBRATE_FACTOR2;
    // factor[3]=CALIBRATE_FACTOR3;

    scale[0]=new HX711(D6,D7);
    scale[1]=new HX711(D4,D5);
    scale[2]=new HX711(D2,D3);
    scale[3]=new HX711(D0,D1);


    for (int s=0; s<4; s++)
    {
        scale[s]->set_scale();
        // Serial.println(s);
        // scale[s]->tare(1);	//Reset the scale to 0
    }
}



// int tarre_countdown=10;
// float prev_total=0;
//
// void tarre()
// {
//     Serial.println("TARRE");
//     for (int s=0; s<4; s++)
//     {
//         scale[s]->set_offset(scale[s]->get_offset()+average[s]);
//         average[s]=0;
//     }
// }

long count=1;
String measurements="[";

void loop() {
    wifi_status();
    ArduinoOTA.handle();

    //collect raw data and send to raw data server for analyses, testing , tuning and simulations
    count++;
    String line;
    // line=line+"["+count;
    line=line+"[";
    for (int s=0; s<4; s++)
    {
        long current=scale[s]->read();
        line=line+current+",";
    }
    line.remove(line.length()-1);
    line=line+"],";
    Serial.println(line);
    measurements=measurements+line;

    if (measurements.length()>=RAW_SIZE)
    {
        //remove final , :
        measurements.remove(measurements.length()-1);
        measurements=measurements+"]";
        HTTPClient http;
        http.begin(RAW_URL);
        http.addHeader("Content-Type", "application/json");
        int httpCode=http.POST(measurements);
        if(httpCode > 0)
        {
            // HTTP header has been send and Server response header has been handled
            Serial.printf("[HTTP] succeeded, code: %d\n", httpCode);

            // file found at server
            if(httpCode == HTTP_CODE_OK) {
                String payload = http.getString();
                Serial.println(payload);
            }
        } else {
            Serial.printf("[HTTP] failed, error: %s\n", http.errorToString(httpCode).c_str());
        }
        http.end();
        measurements="[";
    }


/*
    //we MIGHT use this again in the future, but probably not since collecting data on the server is easier.


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
*/
}
