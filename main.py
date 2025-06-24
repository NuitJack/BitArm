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
    def __init__(self, device_name="PicoBLE"):
        self._SERVICE_UUID = bluetooth.UUID("12345678-1234-5678-1234-56789abcdef0")
        self._CHAR_UUID = bluetooth.UUID("abcdef01-2345-6789-abcd-0123456789ab")
        self.device_name = device_name
        self.conectado = False
        self.characteristic = None
        self.connection = None
        
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

def set_spi_speed(speed, spi):
    spi.init(baudrate=speed)
    
def abrir(cor1, cor2, display):
    display.fill_rect(5, 165, 150, 70, cor1)
    display.fill_rect(165, 165, 150, 70, cor1)
    display.fill_rect(170, 170, 140, 60, cor2)
    display.text('Fechar', 35, 185, fg_color=cor2, bg_color=cor1, scale=3)
    display.text('Aberto', 193, 185, fg_color=cor1, bg_color=cor2, scale=3)

def fechar(cor1, cor2, display):
    display.fill_rect(5, 165, 150, 70, cor1)
    display.fill_rect(165, 165, 150, 70, cor1)
    display.fill_rect(10, 170, 140, 60, cor2)
    display.text('Fechado', 25, 185, fg_color=cor1, bg_color=cor2, scale=3)
    display.text('Abrir', 200, 185, fg_color=cor2, bg_color=cor1, scale=3)
    
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
        
def led(r, g, b, led_r, led_g, led_b):
    led_r.duty_u16(int(r * 65535 / 255))
    led_g.duty_u16(int(g * 65535 / 255))
    led_b.duty_u16(int(b * 65535 / 255))

def play(musica, alto_falante):
    for nota, duracao in musica:
        freq = nota
        alto_falante.freq(freq if freq > 0 else 500)
        alto_falante.duty_u16(32767 if freq > 0 else 0)
        utime.sleep_ms(120 * duracao)
        alto_falante.duty_u16(0)
        utime.sleep_ms(50)

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

def oled_write(s, x, y, oled, fill=False):
    if fill : oled.fill(0)
    oled.text(s, x, y)
    oled.show()
        
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

def tocar_botao(x, y, cor, comp, display, s):
    display.fill_rect(x, y, 80, 80, cor)
    display.fill_rect(x+5, y+5, 80-10, 80-10, comp)
    display.text(s, x + 80//2 - 15, y + 80//2 - 15, fg_color=cor, bg_color=comp, scale=3)
    
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
        
def wait_movement(led_r, led_g, led_b):
    led(100, 100, 0, led_r, led_g, led_b)
    utime.sleep_ms(1000)
    led(0, 0, 50, led_r, led_g, led_b)
    
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
    end = False
    connecting = False
    initialized = False
    BRANCO = 0x0000
    PRETO = 0xFFFF
    CINZA = 0x7BEF
    VERMELHO = 0x07FF
    VERDE = 0xF81F
    rainbow = RainbowColors()
    while not end:
        if not sender.conectado:
            if not connecting:
                oled_write("Conectando", 25, 20, oled)
                oled_write("BLE...", 40, 30, oled)
                led(50, 0, 0, led_r, led_g, led_b)
                connecting = True
            if initialized:
                oled_write("Reconectando", 25, 20, oled)
                oled_write("BLE...", 40, 30, oled)
                led(50, 0, 0, led_r, led_g, led_b)
            await sender.conectar()
        else:
            if not initialized:
                led(0, 0, 50, led_r, led_g, led_b)
                play([(392, 1), (415, 1), (440, 1)], alto_falante)
                oled_write("BLE conectado!", 10, 20, oled, fill=True)
                oled_write("Inicializando", 12, 30, oled)
                display, touch, spi = init(BRANCO, PRETO)
                await asyncio.sleep(2)
                await sender.enviar_caractere('4', oled, 'U1', 40, False)
                await asyncio.sleep(0.5)
                await sender.enviar_caractere('9', oled, 'Abrir', 40, False)
                U1, U2, U3, U4 = False, False, False, False
                D1, D2, D3, D4 = False, False, False, False
                openit, closeit, opened, closed = False, False, True, False
                touched = False
                k, n, ee = 0, 0, 0
                oled_write("Inicializado", 12, 20, oled, fill=True)
                oled_write("com sucesso", 14, 30, oled)
                initialized = True
            if touch.is_touched():
                if k == 200:
                    end = True
                    oled_write("Desconectando", 10, 20, oled, fill=True)
                    oled_write("e encerrando", 12, 30, oled)
                    play([(392, 1), (369, 1), (392, 1), (523, 2)], alto_falante)
                    set_spi_speed(50_000_000, spi)
                    display.fill(PRETO)
                    await sender.desconectar()
                    led(0, 0, 0, led_r, led_g, led_b)
                    oled.fill(0)
                    oled.show()
                if closeit:
                    k += 1
                if not touched:
                    touched = True
                    y, x, z = touch.read()
                    p_x = int(x * 320)
                    p_y = int(y * 240)
                    set_spi_speed(30_000_000, spi)
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
                        closeit = True
                        if closed:
                            tocar_garra(0, VERMELHO, PRETO, display, 'Fechado')
                        else:
                            tocar_garra(0, VERDE, PRETO, display, 'Fechar')
                    elif not openit and 160 <= p_x < 320 and 160 <= p_y < 240: # Open
                        openit = True
                        if opened:
                            tocar_garra(160, VERMELHO, PRETO, display, 'Aberto')
                        else:
                            tocar_garra(160, VERDE, PRETO, display, 'Abrir')
            else:
                touched = False
                if D1:
                    set_spi_speed(50_000_000, spi)
                    D1 = False
                    ee -= 1
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
                    set_spi_speed(50_000_000, spi)
                    closeit = False
                    if opened:
                        fechar(BRANCO, PRETO, display)
                        closed = True
                        opened = False
                        await asyncio.sleep(0.5)
                        await sender.enviar_caractere('8', oled, 'Fechar', 40)
                        wait_movement(led_r, led_g, led_b)
                    else:
                        tocar_garra(0, BRANCO, PRETO, display, 'Fechado')
                        oled_write("Garra foi", 30, 20, oled, fill=True)
                        oled_write("fechada", 38, 30, oled)
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
            set_spi_speed(1_000_000, spi)
        utime.sleep_ms(10)

button_a = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
while not button_a.value() == 0 : utime.sleep_ms(10)
asyncio.run(main())

