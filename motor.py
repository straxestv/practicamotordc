import network
import socket
import time
from machine import Pin, PWM

# ---------------------------
# Configuración WiFi
# ---------------------------
SSID = "GIVE-ME-FREE-LIGMA"
PASSWORD = "nakanoyotsubagod"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

print("Conectando a WiFi...")
while not wlan.isconnected():
    time.sleep(1)

print("Conectado:", wlan.ifconfig())

# ---------------------------
# Configuración del Motor
# ---------------------------
# Usa el canal A del L9110S (pines A-1A y A-1B)
PIN_A = 15  # GPIO para A-1A
PIN_B = 14  # GPIO para A-1B

# Inicializar en LOW para evitar arranque inesperado
pa_pin = Pin(PIN_A, Pin.OUT, value=0)
pb_pin = Pin(PIN_B, Pin.OUT, value=0)
time.sleep(0.05)

in1 = PWM(pa_pin)
in2 = PWM(pb_pin)
in1.freq(1000)
in2.freq(1000)
in1.duty_u16(0)
in2.duty_u16(0)

INVERT = False  # pon True si la velocidad está invertida

def set_motor(velocidad):
    """
    velocidad: -100 .. 100
    positiva = adelante
    negativa = atrás
    0 = stop
    """
    if INVERT:
        velocidad = -velocidad

    if velocidad > 0:
        duty = int(velocidad * 65535 / 100)
        in1.duty_u16(duty)
        in2.duty_u16(0)
    elif velocidad < 0:
        duty = int(abs(velocidad) * 65535 / 100)
        in1.duty_u16(0)
        in2.duty_u16(duty)
    else:
        in1.duty_u16(0)
        in2.duty_u16(0)

# ---------------------------
# Página HTML
# ---------------------------
html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Motor DC</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
    body {
      background-image: url(https://i0.wp.com/elmundodeshiro.link/wp-content/uploads/2025/04/La-famosa-Vtuber-Gawr-Gura-anuncio-su-Retiro.png?w=1920&ssl=1);
      background-repeat: no-repeat; background-size: cover; background-position: center; background-attachment: fixed; font-family: Arial, sans-serif; text-align: center;
    }
    p {
      color: #C908C1;
    }
    
    h2{
     
      color: #C908C1;

    }
    </style>

</head>
<body class="bg-dark text-light text-center">
 <div>
    <img src="https://i.pinimg.com/originals/1e/c2/50/1ec2506e6843eb55d8c21059232333b5.gif" width="280rem" height="190rem">
  </div>
    <div class="container py-4">
        <h1 class="mb-4">Control de Motor DC</h1>

        <label for="velocidad" class="form-label">Velocidad del Motor (%)</label>
        <input type="range" class="form-range" min="-100" max="100" value="0" id="velocidad">

        <p class="mt-3">Velocidad actual: <span id="valor">0</span>%</p>

        <canvas id="indicador" width="200" height="200"></canvas>
    </div>

<script>
const slider = document.getElementById("velocidad");
const valor = document.getElementById("valor");
const ctx = document.getElementById("indicador").getContext("2d");

let chart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ["Velocidad", "Restante"],
        datasets: [{
            data: [0, 100],
            backgroundColor: ["#0d6efd", "#343a40"],
            borderWidth: 1
        }]
    },
    options: {
        circumference: 180,
        rotation: 270,
        cutout: "70%",
        plugins: {legend: {display: false}}
    }
});

slider.addEventListener("input", () => {
    let val = parseInt(slider.value);
    valor.textContent = val;

    fetch(`/set?valor=${val}`);
    
    chart.data.datasets[0].data[0] = Math.abs(val);
    chart.data.datasets[0].data[1] = 100 - Math.abs(val);
    chart.update();
});
</script>
</body>
</html>
"""

# ---------------------------
# Servidor Web
# ---------------------------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("Servidor corriendo en http://", wlan.ifconfig()[0])

while True:
    cl, addr = s.accept()
    print("Cliente conectado:", addr)
    request = cl.recv(1024).decode()

    if "/set?valor=" in request:
        try:
            val_str = request.split("/set?valor=")[1].split(" ")[0]
            val = int(val_str)
            print("Velocidad recibida:", val)
            set_motor(val)
        except:
            pass

    cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()
