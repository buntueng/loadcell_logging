int main_state = 0;
String serial_cmd = "";
bool execute_cmd = false;
bool running_flag = false;
unsigned long loop_timer = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available())
  {
    char input_char = Serial.read();
    if(input_char=='\n')
    {
      execute_cmd = true;
    }
    else
    {
      serial_cmd = serial_cmd + input_char;
    }
  }

  if(execute_cmd)
  {
    if(serial_cmd[0]=='1')
    {
      running_flag = true;
    }
    else
    {
      running_flag = false;
    }
    // clear flag and command
    execute_cmd = false;
    serial_cmd = "";
  }

  if(running_flag)
  {
    int interval = millis()-loop_timer;       // interval not less than 5 milliseconds
      if(interval >=20)
      {
        int input0 = analogRead(A0);
        int input1 = analogRead(A1);
        int input2 = analogRead(A2);
        String loadcell_values = String(input0) + "," + String(input1) + "," + String(input2) + "\n";
        Serial.print(loadcell_values);
        loop_timer = millis();
      }
  }
}
