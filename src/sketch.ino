// meowton - proof of concept for an automatic pet scale

#include "HX711.h"
#include <ESP8266mDNS.h>
#include <ESP8266WiFi.h>
#include "FS.h"
#include <ArduinoOTA.h>
// #include <String>
#include <ESP8266HTTPClient.h>


//send all raw measurement data to this server in json format
//(for analyses or debugging and tuning)
#define RAW_URL "http://192.168.13.22:8080/raw"
// #define RAW_URL "http://192.168.13.236:8080/raw"
//send batches of this many measurements (normally there are 10/s)
#define RAW_COUNT 50


// stop sending data after scale is idle this many mS
#define IDLE_STOP 60000

//amount of noise to ignore for idle detection
#define IDLE_NOISE 10000


//dutycycle function to make stuff blink without using memory
//returns true during 'on' ms, with total periode time 'total' ms.
bool duty_cycle(unsigned long on, unsigned long total, unsigned long starttime=0)
{
  if (!starttime)
    return((millis()%total)<on);
  else
    return(((millis()-starttime)%total)<on);
}



void led_on()
{
  digitalWrite(D8,LOW);
}

void led_off()
{
  digitalWrite(D8,HIGH);
}

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


    scale[0]=new HX711(D6,D7);
    scale[1]=new HX711(D4,D5);
    scale[2]=new HX711(D2,D3);
    scale[3]=new HX711(D0,D1);


    for (int s=0; s<4; s++)
    {
        scale[s]->set_scale();
    }

    pinMode(D8,OUTPUT);
}


long count=0;
String measurements="[";


void send()
{
  if (measurements=="[")
    return;

  Serial.printf("[HTTP] Sending data...\n");
  led_off();

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
      led_on();
  } else {
      Serial.printf("[HTTP] failed, error: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
  measurements="[";

  count=0;

}


long idle_measurement=0;
unsigned long idle_start_time=0;

void loop() {
    wifi_status();
    ArduinoOTA.handle();

    //collect raw data and send to raw data server for analyses, testing , tuning and simulations
    count++;
    String line;
    // line=line+"["+count;
    line=line+"[";
    long measurement=0;
    for (int s=0; s<4; s++)
    {
        long current=scale[s]->read();
        measurement=measurement+current;
        line=line+current+",";
    }
    line.remove(line.length()-1);
    line=line+"],";
    Serial.println(line);

    //idle detection
    if (abs(idle_measurement-measurement)<IDLE_NOISE)
    {
        if (millis()-idle_start_time > IDLE_STOP)
        {
            //idle, send remaining buffer and dont fill it
            send();
            Serial.println("idle");
            if (duty_cycle(100,5000))
              led_on();
            else
              led_off();
            return;
        }
        else
        {
            Serial.print("idle noise:");
            Serial.println(abs(idle_measurement-measurement));

        }
    }
    //not idle anymore
    else
    {
      idle_measurement=measurement;
      idle_start_time=millis();
      Serial.println("idle reset");

    }

    // collect measurement data
    measurements=measurements+line;
    if (count>=RAW_COUNT)
    {
      send();
    }


}
