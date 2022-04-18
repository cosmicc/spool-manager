
#include <HX711_ADC.h>
#include <HTU21D.h>

// Editable Settings

const int HX711_dout = 11; //HX711 dout pin
const int HX711_sck = 10; //HX711 sck pin
unsigned long stabilizingtime = 2000;
float calibrationValue = 401.55;
const int weight_count = 30;

// End of editable settings 

float weights[weight_count];
int mloop = 0;
#define INPUT_SIZE 30

HX711_ADC LoadCell(HX711_dout, HX711_sck);
HTU21D sensor;

void setup() {
  Serial.begin(57600); delay(10);
  Serial.println();
  Serial.println("Starting...");

  LoadCell.begin();
  unsigned long stabilizingtime = 2000;
  LoadCell.start(stabilizingtime, false);
  if (LoadCell.getTareTimeoutFlag()) {
    Serial.println("Sensor Timeout, check HX711 wiring and pin designations. Halting.");
    while(1);
  } else {
    LoadCell.setCalFactor(calibrationValue); // set calibration value (float)
    Serial.println("Startup is complete");
    Serial.println("###");
  }
}

void get_temp() {
  if(sensor.measure()) {
    float temperature = sensor.getTemperature();
    float humidity = sensor.getHumidity();
    Serial.print(temperature);
    Serial.print(':');
    Serial.println(humidity);
  }
}

void take_measurement(float measured_value) {
    //Serial.println(measured_value);
    if (mloop == weight_count) mloop = 0;
    weights[mloop] = measured_value;
    mloop++;     
}

void reset_weights() {
    for (int i = 0; i < weight_count ; i++) weights[i] = 0;
}

void print_weight(){
  float sum = 0;
  for (int i = 0; i < weight_count ; i++) sum += weights[i];
  Serial.println(float(sum / weight_count));
}

void print_list(){
  Serial.print('[');
  for (int i = 0; i < weight_count-1 ; i++) {
    Serial.print(weights[i]);
    Serial.print(',');
  }
  Serial.print(weights[weight_count]);
  Serial.println(']');
}

void calibrate(float cal_weight) {
  Serial.print("Calibrating on ");
  Serial.print(cal_weight);
  Serial.println(" grams...");
  float known_mass = cal_weight;
  bool _resume = false;
  while (_resume == false) {
    LoadCell.update();
      if (known_mass != 0) {
        Serial.print("Known mass is: ");
        Serial.println(known_mass);
        _resume = true;
      }
    }
  LoadCell.refreshDataSet(); //refresh the dataset to be sure that the known mass is measured correct
  float newCalibrationValue = LoadCell.getNewCalibration(known_mass); //get the new calibration value

  Serial.print("New calibration value has been set to: ");
  Serial.println(newCalibrationValue);
  calibrationValue = newCalibrationValue;
  reset_weights();
}


void tare_scale() {
  Serial.println("Taring...");
  LoadCell.tareNoDelay();
}

void spoolmanager(char* cmd, float value) {
  if (strcmp(cmd, "T") == 0) {
    tare_scale();
  } else if (strcmp(cmd, "M") == 0) {
      print_weight();
  } else if (strcmp(cmd, "C") == 0) {
      calibrate(value);
  } else if (strcmp(cmd, "E") == 0) {
      get_temp();
  } else if (strcmp(cmd, "R") == 0) {
      reset_weights();
  } else if (strcmp(cmd, "L") == 0) {
      print_list();
  } else {
    Serial.print("Command not found: ");
    Serial.print(cmd);
    Serial.print(" value: ");
  Serial.println(value);
  }
}

void loop() {
  static boolean newDataReady = 0;
  if (LoadCell.getTareStatus() == true) {
    Serial.println("!");
    reset_weights();
  }
  if (LoadCell.update()) newDataReady = true;
  if (newDataReady) {
      take_measurement(LoadCell.getData());
      newDataReady = 0;
  }
  if (Serial.available() > 0) {
    char input[INPUT_SIZE + 1];
    byte size = Serial.readBytes(input, INPUT_SIZE);
    input[size] = 0;

    // Read each command pair 
    char* command = strtok(input, "&");
    while (command != 0)
    {
      // Split the command in two values
      char* separator = strchr(command, ':');
      if (separator != 0)
      {
        *separator = 0;
        char* cmd = command;
        ++separator;
        float value = atof(separator);
        spoolmanager(cmd, value);
      }
    command = strtok(0, "&");
    }
  }
}
