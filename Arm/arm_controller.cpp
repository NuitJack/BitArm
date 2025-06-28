#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>

// Pinos dos servos
#define BASE_PIN   13
#define BRACO1_PIN 12
#define BRACO2_PIN 14
#define GARRA_PIN  27

// Canais PWM
#define CH_BASE    0
#define CH_BRACO1  1
#define CH_BRACO2  2
#define CH_GARRA   3

// PWM
#define FREQ 50
#define RES 16

// Armazena posição atual (importante para controle parcial da garra)
int posAtual_base   = 90;
int posAtual_braco1 = 90;
int posAtual_braco2 = 90;
int posAtual_garra  = 90;

// Mapeia ângulo para duty (0–180° → duty de 1638 a 8192)
int angleToDuty(int ang) {
  return map(ang, 0, 180, 1638, 8192);
}

// Estrutura de posição
struct Posicao {
  int base;
  int braco1;
  int braco2;
  int garra;
};

// Lista de posições 0–7
Posicao posicoes[8] = {
  { 160, 130, 150, 90 },
  { 120, 130, 150, 90 },
  { 60, 130, 150, 90 },
  { 5, 130, 150, 90 },

  { 160, 100, 120, 90 },
  { 120, 100, 120, 90 },
  { 60, 100, 120, 90 },
  { 5, 100, 120, 90 }
};

void aplicarPosicaoCompleta(const Posicao& alvo) {
  const int delay_ms = 15;
  const int passo = 1;

  int a_base   = posAtual_base;
  int a_braco1 = posAtual_braco1;
  int a_braco2 = posAtual_braco2;
  int a_garra  = posAtual_garra;

  while (a_base != alvo.base || a_braco1 != alvo.braco1 || a_braco2 != alvo.braco2 || a_garra != alvo.garra) {
    if (a_base < alvo.base)   a_base   += passo;
    if (a_base > alvo.base)   a_base   -= passo;

    if (a_braco1 < alvo.braco1) a_braco1 += passo;
    if (a_braco1 > alvo.braco1) a_braco1 -= passo;

    if (a_braco2 < alvo.braco2) a_braco2 += passo;
    if (a_braco2 > alvo.braco2) a_braco2 -= passo;

    if (a_garra < alvo.garra)   a_garra  += passo;
    if (a_garra > alvo.garra)   a_garra  -= passo;

    ledcWrite(CH_BASE,   angleToDuty(a_base));
    ledcWrite(CH_BRACO1, angleToDuty(a_braco1));
    ledcWrite(CH_BRACO2, angleToDuty(a_braco2));
    ledcWrite(CH_GARRA,  angleToDuty(a_garra));

    delay(delay_ms);
  }

  // Atualiza estados finais
  posAtual_base   = alvo.base;
  posAtual_braco1 = alvo.braco1;
  posAtual_braco2 = alvo.braco2;
  posAtual_garra  = alvo.garra;

  Serial.printf("Posição suave concluída: Base=%d, Braço1=%d, Braço2=%d, Garra=%d\n",
                posAtual_base, posAtual_braco1, posAtual_braco2, posAtual_garra);
}

void moverGarraPara(int angGarra) {
  const int delay_ms = 10;
  const int passo = 1;

  int atual = posAtual_garra;
  while (atual != angGarra) {
    if (atual < angGarra) atual += passo;
    else if (atual > angGarra) atual -= passo;

    ledcWrite(CH_GARRA, angleToDuty(atual));
    delay(delay_ms);
  }

  posAtual_garra = angGarra;
  Serial.printf("Garra suavemente ajustada para %d°\n", angGarra);
}


// BLE callback
class ComandoBLE : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pChar) {
    std::string value = pChar->getValue();
    if (value.length() > 0) {
      char cmd = value[0];
      if (cmd >= '0' && cmd <= '7') {
        int idx = cmd - '0';
        aplicarPosicaoCompleta(posicoes[idx]);
      } else if (cmd == '8') {
        moverGarraPara(60);  // Garra aberta
      } else if (cmd == '9') {
        moverGarraPara(120); // Garra fechada
      } else {
        Serial.printf("Comando inválido: %c\n", cmd);
      }
    }
  }
};

void setup() {
  Serial.begin(115200);

  // PWM setup
  ledcSetup(CH_BASE,   FREQ, RES); ledcAttachPin(BASE_PIN,   CH_BASE);
  ledcSetup(CH_BRACO1, FREQ, RES); ledcAttachPin(BRACO1_PIN, CH_BRACO1);
  ledcSetup(CH_BRACO2, FREQ, RES); ledcAttachPin(BRACO2_PIN, CH_BRACO2);
  ledcSetup(CH_GARRA,  FREQ, RES); ledcAttachPin(GARRA_PIN,  CH_GARRA);

  // BLE
  BLEDevice::init("ESP32_BRAÇO_BLE");
  BLEServer *server = BLEDevice::createServer();
  BLEService *service = server->createService("12345678-1234-5678-1234-56789abcdef0");
  BLECharacteristic *charac = service->createCharacteristic(
    "abcdef01-2345-6789-abcd-0123456789ab",
    BLECharacteristic::PROPERTY_WRITE
  );
  charac->setCallbacks(new ComandoBLE());
  service->start();
  server->getAdvertising()->start();

  Serial.println("BLE pronto. Envie caracteres '0' a '9' para controle.");
}

void loop() {
  // nada
}
