#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

const int TRIG_PIN = 3;
const int ECHO_PIN = 2;

const int ENA = 11;
const int IN1 = 12;
const int IN2 = 13;

#define BASE_CH     0
#define SHOULDER_CH 1
#define ELBOW_CH    2
#define GRIP_CH     3

#define SERVOMIN 130
#define SERVOMAX 620

String inputString = "";
int currentAngle[4] = {90, 90, 90, 90};
int counter = 0;
int count = 0;
bool objectHandled = false;

void setup() {
  Serial.begin(9600);
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  pwm.begin();
  pwm.setPWMFreq(60);
  moveToHome();
}

void loop() {
  float distance = ultrasonik(TRIG_PIN, ECHO_PIN);

  if (distance <= 15) {
    count++;
    if (count >= 70) {
      counter++;
      count = 0;
    }

    if (counter == 0) {
      ControllMotor(150, 1);
    }

    if (counter >= 1 && !objectHandled) {
      ControllMotor(0, 0);
      float data = DataKamera();
      delay(10000);
      if (data != 0) { // hanya lanjut jika data valid
        Objek((int)data);
        objectHandled = true;
      }
    }

  } else {
    ControllMotor(100, 1);
    moveToHome();
    counter = 0;
    count = 0;
    objectHandled = false;
  }
}

// ========== Fungsi Servo ==========

void moveServoSmooth(uint8_t channel, int targetAngle, int delayTime) {
  targetAngle = constrain(targetAngle, 0, 180);
  int step = (targetAngle > currentAngle[channel]) ? 1 : -1;

  for (int angle = currentAngle[channel]; angle != targetAngle; angle += step) {
    int pulse = map(angle, 0, 180, SERVOMIN, SERVOMAX);
    pwm.setPWM(channel, 0, pulse);
    delay(delayTime);
  }

  int finalPulse = map(targetAngle, 0, 180, SERVOMIN, SERVOMAX);
  pwm.setPWM(channel, 0, finalPulse);
  currentAngle[channel] = targetAngle;
}

void moveToHome() {
  moveServoSmooth(BASE_CH, 70, 5);
  moveServoSmooth(SHOULDER_CH, 100, 5);
  moveServoSmooth(ELBOW_CH, 130, 5);
  moveServoSmooth(GRIP_CH, 35, 5);
}

// ========== Fungsi Utama Aksi ==========

void Objek(int jenis) {
  int base;
  if (jenis == 1) base = 180;            // matang
  else if (jenis == 2) base = 150;       // setengah matang
  else if (jenis == 3) base = 0;         // mentah
  else return;                           // data tidak valid

  // Ambil objek
  moveServoSmooth(BASE_CH, 70, 5);
  moveServoSmooth(SHOULDER_CH, 178, 5);
  moveServoSmooth(ELBOW_CH, 120, 5);
  delay(500);
  moveServoSmooth(GRIP_CH, 60, 5);
  delay(500);

  // Angkat
  moveServoSmooth(SHOULDER_CH, 100, 5);
  moveServoSmooth(ELBOW_CH, 130, 5);
  delay(300);

  // Putar ke tempat tujuan
  moveServoSmooth(BASE_CH, base, 5);
  moveServoSmooth(SHOULDER_CH, 178, 5);
  moveServoSmooth(ELBOW_CH, 120, 5);
  delay(500);
  moveServoSmooth(GRIP_CH, 30, 5); // lepas
  delay(300);
  moveServoSmooth(SHOULDER_CH, 100, 5);
  moveServoSmooth(ELBOW_CH, 130, 5);
  delay(300);
  // Kembali ke home
  moveToHome();
}

// ========== Fungsi Motor & Sensor ==========

void ControllMotor(int speed, int direction) {
  analogWrite(ENA, speed);
  if (direction == 1) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else if (direction == 2) {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
  }
}

float ultrasonik(int trigPin, int echoPin) {
  pinMode(trigPin, OUTPUT);
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  pinMode(echoPin, INPUT);
  long duration = pulseIn(echoPin, HIGH, 20000);
  float distance = duration * 0.034 / 2.0;
  return distance;
}

// ========== Fungsi Data Kamera ==========

float DataKamera() {
  if (Serial.available()) {
    inputString = Serial.readStringUntil('\n');
    inputString.trim();

    if (inputString == "matang") {
      Serial.println("Data: matang");
      return 1;
    } else if (inputString == "setengah_matang") {
      Serial.println("Data: setengah matang");
      return 2;
    } else if (inputString == "mentah") {
      Serial.println("Data: mentah");
      return 3;
    } else {
      Serial.println("Data tidak dikenali");
    }
  }
  return 0; // default: data tidak valid
}
