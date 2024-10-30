#include <LoRa.h>
#include "LoRaBoards.h"
#include "ClosedCube_HDC1080.h" //Librería que permite incluir las funciones del sensor de temperatura y humedad.
#include <TinyGPSPlus.h> //Librería que permite incluir las funciones del GPS.

//Declaración de funciones
void prunning();
float temperatura(int nro_temps);
float humedad(int nro_hums);
float* gpsData();
void bundling(float temp, float hum, float* gps);
static void smartDelay(unsigned long ms);

#ifndef CONFIG_RADIO_FREQ
#define CONFIG_RADIO_FREQ           915.0
#endif
#ifndef CONFIG_RADIO_OUTPUT_POWER
#define CONFIG_RADIO_OUTPUT_POWER   17
#endif
#ifndef CONFIG_RADIO_BW
#define CONFIG_RADIO_BW             125.0
#endif


#if !defined(USING_SX1276) && !defined(USING_SX1278)
#error "LoRa example is only allowed to run SX1276/78. For other RF models, please run examples/RadioLibExamples"
#endif


//LoRa
const char* host = "10.38.32.137"; //direccion ip publica del servidor (maquina virtual)
const uint16_t port = 8080; //puerto por el cual me voy a conectar

//Temperatura y Humedad
ClosedCube_HDC1080 sensor;

//GPS
TinyGPSPlus gps;

int counter = 0;

void setup()
{
    sensor.begin(0x40);
    smartDelay(20);

    Serial.begin(115200); //Iniciar la comunicación serial (me conecto a capa 2)
    Serial1.begin(9600, SERIAL_8N1, 34, 12); //Comunicación con el GPS (baudrate, protocolo, rx, tx)
    smartDelay(20);

    setupBoards();
    // When the power is turned on, a delay is required.
    delay(1500);

    #ifdef  RADIO_TCXO_ENABLE
        pinMode(RADIO_TCXO_ENABLE, OUTPUT);
        digitalWrite(RADIO_TCXO_ENABLE, HIGH);
    #endif

    Serial.println("LoRa Sender");
    LoRa.setPins(RADIO_CS_PIN, RADIO_RST_PIN, RADIO_DIO0_PIN);
    if (!LoRa.begin(CONFIG_RADIO_FREQ * 1000000)) {
        Serial.println("Starting LoRa failed!");
        while (1);
    }

    LoRa.setTxPower(CONFIG_RADIO_OUTPUT_POWER);
    LoRa.setSignalBandwidth(CONFIG_RADIO_BW * 1000);
    LoRa.setSpreadingFactor(10);
    LoRa.setPreambleLength(16);
    LoRa.setSyncWord(0xAB);
    LoRa.disableCrc();
    LoRa.disableInvertIQ();
    LoRa.setCodingRate4(7);
}

void loop()
{
    float temp = temperatura(3);
    float hum = humedad(3);
    float* gps = gpsData();
    
    //Medición de temperatura y humedad
    Serial.printf("Temperatura: %.2f C\n", temp);
    Serial.printf("Humedad: %.2f %%\n", hum);

    //Medición de GPS
    Serial.printf("Latitud: %f\n", gps[0]);
    Serial.printf("Longitud: %f\n", gps[1]);

    //Envío de datos al servidor
    bundling(temp, hum, gps);

    for (int i = 0; i < 18; i++){
        smartDelay(500); //La suma de los SmartDelay es 9 segundos, calculando la temperatura, humedad y posición me gasto 1 segundo.
    }
}


//Prunning
float prunning(float datos[], float len){
  
  float total = 0;
  for (int i = 0; i < len; i++)
  {
    total += datos[i];
  }
  return (total/len);
  
}

//Obtener temperatura (prunning incluido)
float temperatura(int nro_temps){

  float temp = 0;
  float temperaturas[nro_temps] = {};

  for (int i = 0; i < nro_temps; i++)
  {
    temp = sensor.readTemperature();
    smartDelay(100);
    temperaturas[i] = temp;
  }

  float promedio = prunning(temperaturas, nro_temps);
  return promedio;
}

//Obtener humedad (prunning incluido)
float humedad(int nro_hums){

  float hum = 0;
  float humedades[nro_hums] = {};

  for (int i = 0; i < nro_hums; i++)
  {
    hum = sensor.readHumidity();
    smartDelay(100);
    humedades[i] = hum;
  }

  float promedio = prunning(humedades, nro_hums);
  return promedio;
}

//Obtener datos del GPS
float* gpsData(){
  smartDelay(400);
  float* data = new float[2];

  if(gps.location.isUpdated()){
    data[0] = gps.location.lat();
    data[1] = gps.location.lng();
  }
  return data;
}

//Envío de datos
void bundling(float temp, float hum, float* gps){

    Serial.print("Sending packet: ");
    Serial.println(counter);

    //Mensaje a enviar
    String message = "Saimon${\"lat\": {\"value\":" +  String(gps[0], 6) + "},\"lon\": {\"value\":" + String(gps[1], 6) + "},\"temp\": {\"value\":" + String(temp, 2) + "},\"humedad\": {\"value\":" + String(hum, 2) + "}}";
    Serial.println( message);

    //send packet
    LoRa.beginPacket();
    LoRa.print(message);
    LoRa.endPacket();

    counter++;
    delay(5000); //Cambiar para enviar cada 5 min
}

static void smartDelay(unsigned long ms)
{
  unsigned long start = millis();
  do
  {
    while (Serial1.available())
      gps.encode(Serial1.read());
  } while (millis() - start < ms);
}