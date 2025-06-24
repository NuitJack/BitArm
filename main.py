import aioble
import bluetooth
import struct
import uasyncio as asyncio
import machine
import utime
from ili9341 import ILI9341
from tsc2046 import TSC2046
from ssd1306 import SSD1306_I2C

class BLE_Sender:
    
    # Inicializa os parâmetros de conexão necessários para a comunicação com a ESP32
    def __init__(self, device_name="PicoBLE"):
        self._SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
        self._CHAR_UUID = bluetooth.UUID("abcdef01-2345-6789-abcd-0123456789ab")
        self.device_name = device_name
        self.conectado = False
        self.characteristic = None
        self.connection = None

    # Rotina de conexão com a ESP32
    async def conectar(self):
        print("Procurando ESP32...")
        device = None
        try:
            # Scan por 5 segundos (5000ms), com janela de 3 segundos (3000ms)
            async with aioble.scan(5000, 3000) as scanner:
                async for result in scanner:
                    print("Dispositivo encontrado:", result.name())
                    if result.name() == "ESP32_BRAÇO_BLE":
                        print("ESP32 encontrada!")
                        device = result.device
                        break
            if not device:
                print("ESP32 não encontrada.")
                return False
            print("Conectando...")
            try:
                # Tentar conectar com timeout de 10 segundos
                self.connection = await asyncio.wait_for(device.connect(), 10)
                print("Conectado, buscando serviços...")
                service = await self.connection.service(self._SERVICE_UUID)
                self.characteristic = await service.characteristic(self._CHAR_UUID)
                utime.sleep_ms(3000)
                self.conectado = True
                print("Conectado com sucesso!")
                return True
                
            except asyncio.TimeoutError:
                print("Timeout na conexão")
                return False
            except Exception as e:
                print("Erro durante conexão:", e)
                return False
                
        except Exception as e:
            print("Erro durante scan:", e)
            return False

    # Rotina de desconexão com a ESP32
    async def desconectar(self):
        if self.connection:
            try:
                await self.connection.disconnect()
            except:
                pass
        self.connection = None
        self.characteristic = None
        self.conectado = False
        print("Desconectado.")

    # Rotina de envio de caracteres para a ESP32. Todos os comandos comunicáveis estão codificados nos caracteres numéricos de 0 a 9. Essa rotina também exibe no OLED o comando enviado
    async def enviar_caractere(self, caractere, oled, s, x, oled_print=True):
        if not self.conectado or self.characteristic is None:
            print(f"Erro: Não conectado a dispositivo BLE ou dispositivo não disponível {self.conectado} {self.characteristic}")
            return False
        try:
            dados = str(caractere).encode('utf-8')
            
            await self.characteristic.write(dados, True)
            if oled_print:
                oled_write("Comando enviado:", 0, 20, oled, fill=True)
                oled_write(s, x, 30, oled)
            print(f"Caractere '{caractere}' enviado")
            return True
        except Exception as e:
            if e is not None:
                print(f"Erro ao enviar caractere '{caractere}':", e)
                return False

# Rotina necessária uma vez que o barramento SPI é compartilhado tanto para o touch (mais lento) quanto para o LCD (mais rápido)
def set_spi_speed(speed, spi):
    spi.init(baudrate=speed)

# Rotina que implementa a animação de exibição dos dois botões superiores (estado: fechar/aberto)
def abrir(cor1, cor2, display):
    display.fill_rect(5, 165, 150, 70, cor1)
    display.fill_rect(165, 165, 150, 70, cor1)
    display.fill_rect(170, 170, 140, 60, cor2)
    display.text('Fechar', 35, 185, fg_color=cor2, bg_color=cor1, scale=3)
    display.text('Aberto', 193, 185, fg_color=cor1, bg_color=cor2, scale=3)

# Rotina que implementa a animação de exibição dos dois botões superiores (estado: fechado/abrir)
def fechar(cor1, cor2, display):
    display.fill_rect(5, 165, 150, 70, cor1)
    display.fill_rect(165, 165, 150, 70, cor1)
    display.fill_rect(10, 170, 140, 60, cor2)
    display.text('Fechado', 25, 185, fg_color=cor1, bg_color=cor2, scale=3)
    display.text('Abrir', 200, 185, fg_color=cor2, bg_color=cor1, scale=3)

# Rotina que implementa a animação de exibição dos oito botões inferiores
def montar_botoes(cor1, cor2, display, fill=True):
    if fill : display.fill(cor2)
    largura_quadrado = 320 // 4
    altura_quadrado = 240 // 3
    s = "D"
    for linha in range(2):
        k = '1'
        for coluna in range(4):
            s += k
            k = str(int(k) + 1)
            x = coluna * largura_quadrado
            y = linha * altura_quadrado
            if (linha + coluna) % 2 == 0:
                cor = cor1
                comp = cor2
            else:
                cor = cor2
                comp = cor1
            display.fill_rect(x, y, largura_quadrado, altura_quadrado, cor)
            display.fill_rect(x+5, y+5, largura_quadrado-10, altura_quadrado-10, comp)
            display.text(s, x + largura_quadrado//2 - 15, y + altura_quadrado//2 - 15, fg_color=cor, bg_color=comp, scale=3)
            s = s[:-1]
        s = "U"

# Rotina que muda a cor do led da BitDogLab
def led(r, g, b, led_r, led_g, led_b):
    led_r.duty_u16(int(r * 65535 / 255))
    led_g.duty_u16(int(g * 65535 / 255))
    led_b.duty_u16(int(b * 65535 / 255))
    
# Rotina que toca uma música (escrita em duty cycles) nos auto falantes da BitDogLab
def play(musica, alto_falante):
    for nota, duracao in musica:
        freq = nota
        alto_falante.freq(freq if freq > 0 else 500)
        alto_falante.duty_u16(32767 if freq > 0 else 0)
        utime.sleep_ms(120 * duracao)
        alto_falante.duty_u16(0)
        utime.sleep_ms(50)

# Rotina que escreve um texto s a partir da coordenada x y no display OLED da BitDogLab
def oled_write(s, x, y, oled, fill=False):
    if fill : oled.fill(0)
    oled.text(s, x, y)
    oled.show()

# Rotina que inicializa todos os periféicos da BitDogLab que são utilizados no projeto
def init_bitdog():
    led_r = machine.PWM(machine.Pin(12))
    led_g = machine.PWM(machine.Pin(11))
    led_b = machine.PWM(machine.Pin(13))
    alto_falante = machine.PWM(machine.Pin(4))
    led_r.freq(1000)
    led_g.freq(1000)
    led_b.freq(1000)
    i2c_oled = machine.SoftI2C(scl=machine.Pin(15), sda=machine.Pin(14))
    oled = SSD1306_I2C(128, 64, i2c_oled)
    oled.fill(0)
    oled.show()
    return led_r, led_g, led_b, alto_falante, oled

# Rotina de inicialização da comunicação SPI, do LCD e do touch, além das devidas calibrações e uma primeira exibição dos botões.
def init(cor1, cor2):
    spi = machine.SPI(0,
                      baudrate=30_000_000,
                      sck=machine.Pin(18),
                      mosi=machine.Pin(19),
                      miso=machine.Pin(16))
    display = ILI9341(spi, 
                      dc=machine.Pin(20),
                      cs=machine.Pin(17),
                      WIDTH=320,
                      HEIGHT=240,
                      rst=None)
    montar_botoes(cor1, cor2, display)
    abrir(cor1, cor2, display)
    set_spi_speed(1_000_000, spi)
    touch = TSC2046(spi,
                    cs=machine.Pin(9),
                    irq=None)
    CALIB_X_MIN = 1880
    CALIB_X_MAX = 150
    CALIB_Y_MIN = 270
    CALIB_Y_MAX = 1830
    touch.set_calibration((CALIB_X_MIN, CALIB_X_MAX, CALIB_Y_MIN, CALIB_Y_MAX))
    return display, touch, spi

# Animação responsável pela responsividade dos dois botões superiores
def tocar_garra(x, cor1, cor2, display, s):
    display.fill_rect(x+5, 165, 150, 70, cor1)
    if s == 'Fechar':
        display.text('Fechar', 35, 185, fg_color=cor2, bg_color=cor1, scale=3)
    elif s == 'Fechado':
        display.fill_rect(x+10, 170, 140, 60, cor2)
        display.text('Fechado', 25, 185, fg_color=cor1, bg_color=cor2, scale=3)
    elif s == 'Abrir':
        display.text('Abrir', 200, 185, fg_color=cor2, bg_color=cor1, scale=3)
    elif s == 'Aberto':
        display.fill_rect(x+10, 170, 140, 60, cor2)
        display.text('Aberto', 193, 185, fg_color=cor1, bg_color=cor2, scale=3)

# Animação responsável pela responsividade dos oito botões inferiores
def tocar_botao(x, y, cor, comp, display, s):
    display.fill_rect(x, y, 80, 80, cor)
    display.fill_rect(x+5, y+5, 80-10, 80-10, comp)
    display.text(s, x + 80//2 - 15, y + 80//2 - 15, fg_color=cor, bg_color=comp, scale=3)

# Animação do led da BitDogLab responsável pelo halt do programa durante o movimento do braço robótico, aguardando por um segundo
def wait_movement(led_r, led_g, led_b):
    led(100, 100, 0, led_r, led_g, led_b)
    utime.sleep_ms(1000)
    led(0, 0, 50, led_r, led_g, led_b)

# EasterEgg
class RainbowColors():
    def __init__(self):
        self.color = 0x0000
    def next(self):
        if self.color == 0xFFFF : self.color = 0x0000
        else : self.color += 0xA
        return self.color

async def main():
    led_r, led_g, led_b, alto_falante, oled = init_bitdog()
    sender = BLE_Sender("Touch-Interface")
    # Flags
    end = False           # indica se o usuário pediu o encerramento da execução
    connecting = False    # indica se o texto "Conectando BLE..." já foi escrito no OLED
    initialized = False   # indica se as rotinas de inicialização já foram executadas
    # Cores
    BRANCO = 0x0000
    PRETO = 0xFFFF
    CINZA = 0x7BEF
    VERMELHO = 0x07FF
    VERDE = 0xF81F
    # EasterEgg
    rainbow = RainbowColors()
    while not end:
        if not sender.conectado:
            if not connecting:
                # Escrita no OLED para feedback ao usuário durante espera pela conexão à ESP32
                oled_write("Conectando", 25, 20, oled)
                oled_write("BLE...", 40, 30, oled)
                led(50, 0, 0, led_r, led_g, led_b)
                # Só precisa ser exibido uma vez, logo:
                connecting = True
            if initialized:
                # Caso a conexão caia, escreve no OLED para feedback ao usuário
                oled_write("Reconectando", 25, 20, oled)
                oled_write("BLE...", 40, 30, oled)
                led(50, 0, 0, led_r, led_g, led_b)
            # Solicitação de conexão
            await sender.conectar()
        else:
            if not initialized:
                # Rotinas de inicialização:
                led(0, 0, 50, led_r, led_g, led_b)                            # Led azul acende para indicar conexão bem sucedida
                play([(392, 1), (415, 1), (440, 1)], alto_falante)            # Música para indicar conexão bem sucedida
                oled_write("BLE conectado!", 10, 20, oled, fill=True)         # Escrita no OLED para indicar conexão bem sucedida
                oled_write("Inicializando", 12, 30, oled)
                display, touch, spi = init(BRANCO, PRETO)                     # Inicialização do SPI, touch e LCD
                await asyncio.sleep(2)                                        # Espera pela inicialização
                await sender.enviar_caractere('4', oled, 'U1', 40, False)     # Posição inicial: 4 ("U1")
                await asyncio.sleep(0.5)
                await sender.enviar_caractere('9', oled, 'Abrir', 40, False)  # Posição inicial: 9 (Garra aberta)
                # Flags para lógica de toque ("anti bouncing")
                U1, U2, U3, U4 = False, False, False, False
                D1, D2, D3, D4 = False, False, False, False
                # Flags específicas
                openit, closeit, opened, closed = False, False, True, False
                touched = False
                # Temporizações incrementais
                k, n, ee = 0, 0, 0
                # Feedback de fim da inicialização no OLED
                oled_write("Inicializado", 12, 20, oled, fill=True)
                oled_write("com sucesso", 14, 30, oled)
                initialized = True
            # Lógicas de código a serem executadas durante o toque
            if touch.is_touched():
                # Se o contador de encerramento tiver chegado em 200 (~2s)
                if k == 200:
                    # Rotina de encerramento
                    end = True
                    oled_write("Desconectando", 10, 20, oled, fill=True)            # Feedback visual no OLED
                    oled_write("e encerrando", 12, 30, oled)
                    play([(392, 1), (369, 1), (392, 1), (523, 2)], alto_falante)    # Música de encerramento
                    set_spi_speed(50_000_000, spi)
                    display.fill(PRETO)                                             # Apagar display LCD
                    await sender.desconectar()                                      # Encerrar BLE
                    led(0, 0, 0, led_r, led_g, led_b)                               # Apagar led da BitDogLab
                    oled.fill(0)                                                    # Apagar OLED
                    oled.show()
                # Se o toque tem o intuito de fechar
                if closeit:
                    k += 1
                # Se o botão acabou de ser tocado
                if not touched:
                    # Atualiza flag
                    touched = True
                    # Lê a posição do toque
                    y, x, z = touch.read()
                    p_x = int(x * 320)
                    p_y = int(y * 240)
                    # Acelera para animações
                    set_spi_speed(30_000_000, spi)
                    # Lógica de detecção do toque por pooling. Todos atualizam flags para animações e demais lógicas
                    if not D1 and 0 <= p_x < 80 and 0 <= p_y < 80: # D1
                        tocar_botao(0, 0, VERDE, PRETO, display, 'D1')
                        D1 = True
                    elif not D2 and 80 <= p_x < 160 and 0 <= p_y < 80: # D2
                        tocar_botao(80, 0, PRETO, VERDE, display, 'D2')
                        D2 = True
                    elif not D3 and 160 <= p_x < 240 and 0 <= p_y < 80: # D3
                        tocar_botao(160, 0, VERDE, PRETO, display, 'D3')
                        D3 = True
                    elif not D4 and 240 <= p_x < 320 and 0 <= p_y < 80: # D4
                        tocar_botao(240, 0, PRETO, VERDE, display, 'D4')
                        D4 = True
                    elif not U1 and 0 <= p_x < 80 and 80 <= p_y < 160: # U1
                        tocar_botao(0, 80, PRETO, VERDE, display, 'U1')
                        U1 = True
                    elif not U2 and 80 <= p_x < 160 and 80 <= p_y < 160: # U2
                        tocar_botao(80, 80, VERDE, PRETO, display, 'U2')
                        U2 = True
                    elif not U3 and 160 <= p_x < 240 and 80 <= p_y < 160: # U3
                        tocar_botao(160, 80, PRETO, VERDE, display, 'U3')
                        U3 = True
                    elif not U4 and 240 <= p_x < 320 and 80 <= p_y < 160: # U4
                        tocar_botao(240, 80, VERDE, PRETO, display, 'U4')
                        U4 = True
                    elif not closeit and 0 <= p_x < 160 and 160 <= p_y < 240: # Close
                        # Flag identifica intuito de fechar
                        closeit = True
                        if closed:
                            tocar_garra(0, VERMELHO, PRETO, display, 'Fechado')
                        else:
                            tocar_garra(0, VERDE, PRETO, display, 'Fechar')
                    elif not openit and 160 <= p_x < 320 and 160 <= p_y < 240: # Open
                        # Flag identifica intuito de abrir
                        openit = True
                        if opened:
                            tocar_garra(160, VERMELHO, PRETO, display, 'Aberto')
                        else:
                            tocar_garra(160, VERDE, PRETO, display, 'Abrir')
            else:
                # Atualiza flag
                touched = False
                # Pooling para animações que disparam ao soltar o botão. Todos os oito botões inferiores são iguais
                if D1:
                    # Acelera SPI
                    set_spi_speed(50_000_000, spi)
                    # Atualzia flag
                    D1 = False
                    # EasterEgg counter
                    ee -= 1
                    # Animações e envio do caractere
                    tocar_botao(0, 0, BRANCO, PRETO, display, 'D1')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('0', oled, 'D1', 50)
                    wait_movement(led_r, led_g, led_b)
                elif D2:
                    set_spi_speed(50_000_000, spi)
                    D2 = False
                    tocar_botao(80, 0, PRETO, BRANCO, display, 'D2')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('1', oled, 'D2', 50)
                    wait_movement(led_r, led_g, led_b)
                elif D3:
                    set_spi_speed(50_000_000, spi)
                    D3 = False
                    tocar_botao(160, 0, BRANCO, PRETO, display, 'D3')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('2', oled, 'D3', 50)
                    wait_movement(led_r, led_g, led_b)
                elif D4:
                    set_spi_speed(50_000_000, spi)
                    D4 = False
                    tocar_botao(240, 0, PRETO, BRANCO, display, 'D4')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('3', oled, 'D4', 50)
                    wait_movement(led_r, led_g, led_b)
                elif U1:
                    set_spi_speed(50_000_000, spi)
                    U1 = False
                    # EasterEgg counter
                    ee += 1
                    tocar_botao(0, 80, PRETO, BRANCO, display, 'U1')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('4', oled, 'U1', 50)
                    wait_movement(led_r, led_g, led_b)
                elif U2:
                    set_spi_speed(50_000_000, spi)
                    U2 = False
                    tocar_botao(80, 80, BRANCO, PRETO, display, 'U2')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('5', oled, 'U2', 50)
                    wait_movement(led_r, led_g, led_b)
                elif U3:
                    set_spi_speed(50_000_000, spi)
                    U3 = False
                    tocar_botao(160, 80, PRETO, BRANCO, display, 'U3')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('6', oled, 'U3', 50)
                    wait_movement(led_r, led_g, led_b)
                elif U4:
                    set_spi_speed(50_000_000, spi)
                    U4 = False
                    tocar_botao(240, 80, BRANCO, PRETO, display, 'U4')
                    await asyncio.sleep(0.5)
                    await sender.enviar_caractere('7', oled, 'U4', 50)
                    wait_movement(led_r, led_g, led_b)
                elif closeit:
                    # Acelera SPI
                    set_spi_speed(50_000_000, spi)
                    # Atualiza flag
                    closeit = False
                    # Se estava aberto, o intuito de fechar realmente fecha
                    if opened:
                        # Animação
                        fechar(BRANCO, PRETO, display)
                        # Atualização de flags de estado
                        closed = True
                        opened = False
                        await asyncio.sleep(0.5)
                        # Envio de caractere
                        await sender.enviar_caractere('8', oled, 'Fechar', 40)
                        wait_movement(led_r, led_g, led_b)
                    # Se já estava fechado, intuito de fechar não manda caractere
                    else:
                        # Animação e feedback visual no OLED
                        tocar_garra(0, BRANCO, PRETO, display, 'Fechado')
                        oled_write("Garra foi", 30, 20, oled, fill=True)
                        oled_write("fechada", 38, 30, oled)
                # Lógica análoga ao closeit
                elif openit:
                    set_spi_speed(50_000_000, spi)
                    openit = False
                    if closed:
                        abrir(BRANCO, PRETO, display)
                        opened = True
                        closed = False
                        await asyncio.sleep(0.5)
                        await sender.enviar_caractere('9', oled, 'Abrir', 40)
                        wait_movement(led_r, led_g, led_b)
                    else:
                        tocar_garra(160, BRANCO, PRETO, display, 'Aberto')
                        oled_write("Garra foi", 30, 20, oled, fill=True)
                        oled_write("aberta", 40, 30, oled)
            # EasterEgg
            if ee >= 3:
                ee = 3
                if n%100 == 0:
                    print("Rainbow mode!")
                    BRANCO = rainbow.next()
                    set_spi_speed(50_000_000, spi)
                    montar_botoes(BRANCO, PRETO, display, fill=False)
                    if opened : abrir(BRANCO, PRETO, display)
                    if closed : fechar(BRANCO, PRETO, display)
                    set_spi_speed(1_000_000, spi)
                n += 1
            elif ee < 0 : ee = 0
            elif BRANCO != 0x0000:
                BRANCO = 0x0000
                ee = 0
            # Diminuição da velocidade para touch
            set_spi_speed(1_000_000, spi)
        # "Taxa de atualização" de pooling: 100Hz
        utime.sleep_ms(10)

# Programa não inicia enquanto o botão A não for pressionado
button_a = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
while not button_a.value() == 0 : utime.sleep_ms(10)
asyncio.run(main())
