import network                       # importa el módulo para manejar la interfaz Wi-Fi en MicroPython
import socket                        # importa sockets para crear el servidor web (TCP)
import time                          # importa time para usar time.sleep()
from machine import Pin, PWM         # importa Pin y PWM para controlar GPIO y generar PWM

# ---------------------------
# Configuración WiFi
# ---------------------------
SSID = "Nombre de tu red"         # nombre de la red Wi-Fi a la que la Pico intentará conectarse
PASSWORD = "contraseña de tu red"       # contraseña de la red Wi-Fi

wlan = network.WLAN(network.STA_IF) # crea la interfaz Wi-Fi en modo estación (conectar a un router)
wlan.active(True)                   # activa la interfaz Wi-Fi
wlan.connect(SSID, PASSWORD)        # inicia la conexión a la red Wi-Fi usando SSID y PASSWORD

print("Conectando a WiFi...")       # mensaje en consola indicando que se está intentando conectar
while not wlan.isconnected():       # bucle bloqueante: espera hasta que la Pico obtenga conexión IP
    time.sleep(1)                   # espera 1 segundo antes de comprobar otra vez

print("Conectado:", wlan.ifconfig())# una vez conectado, muestra la configuración de red (IP, máscara, gateway, DNS)

# ---------------------------
# Configuración del Motor
# ---------------------------
# Usa el canal A del L9110S (pines A-1A y A-1B)
PIN_A = 15  # GPIO para A-1A         # define el GPIO de la Pico conectado a la entrada A-1A del L9110S
PIN_B = 14  # GPIO para A-1B         # define el GPIO de la Pico conectado a la entrada A-1B del L9110S

# Inicializar en LOW para evitar arranque inesperado
pa_pin = Pin(PIN_A, Pin.OUT, value=0) # configura PIN_A como salida y lo pone en 0 (evita estado flotante)
pb_pin = Pin(PIN_B, Pin.OUT, value=0) # configura PIN_B como salida y lo pone en 0 (evita estado flotante)
time.sleep(0.05)                       # pequeña pausa para asegurar que las salidas se estabilicen

in1 = PWM(pa_pin)                      # crea objeto PWM sobre el pin A (ahora como PWM)
in2 = PWM(pb_pin)                      # crea objeto PWM sobre el pin B (ahora como PWM)
in1.freq(1000)                         # establece la frecuencia PWM en 1000 Hz para in1
in2.freq(1000)                         # establece la frecuencia PWM en 1000 Hz para in2
in1.duty_u16(0)                        # fija duty 0 inicial en in1 (motor detenido)
in2.duty_u16(0)                        # fija duty 0 inicial en in2 (motor detenido)

INVERT = False  # pon True si la velocidad está invertida  # bandera para invertir la dirección sin cambiar cableado

def set_motor(velocidad):              # función para controlar motor; recibe velocidad en -100 .. 100
    """
    velocidad: -100 .. 100
    positiva = adelante
    negativa = atrás
    0 = stop
    """
    if INVERT:                         # si la bandera INVERT está activada
        velocidad = -velocidad         # invierte la señal de velocidad (corrige lógica física)

    if velocidad > 0:                  # caso: velocidad positiva -> girar adelante
        duty = int(velocidad * 65535 / 100)  # mapear porcentaje (0..100) a rango duty_u16 (0..65535)
        in1.duty_u16(duty)             # aplica PWM a in1 para avanzar
        in2.duty_u16(0)                # in2 en 0 para evitar frenado o invertir
    elif velocidad < 0:                # caso: velocidad negativa -> girar atrás
        duty = int(abs(velocidad) * 65535 / 100)  # calcular magnitud y mapear a duty
        in1.duty_u16(0)                # in1 en 0
        in2.duty_u16(duty)             # aplica PWM a in2 para invertir sentido
    else:                              # caso: velocidad == 0 -> detener motor
        in1.duty_u16(0)                # ambos a 0 => motor en coast (libre)
        in2.duty_u16(0)

# ---------------------------
# Página HTML
# ---------------------------
html = """<!DOCTYPE html> <!-- declara el tipo de documento HTML5 -->
<html lang="es"> <!-- documento en español -->
<head>
    <meta charset="UTF-8"> <!-- codificación UTF-8 -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0"> <!-- responsive -->
    <title>Control Motor DC</title> <!-- título de la página -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"> <!-- carga Bootstrap desde CDN para estilos -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script> <!-- carga Chart.js desde CDN para el gráfico -->
    <style>
    body {
      background-image: url(https://i0.wp.com/elmundodeshiro.link/wp-content/uploads/2025/04/La-famosa-Vtuber-Gawr-Gura-anuncio-su-Retiro.png?w=1920&ssl=1); <!-- imagen de fondo -->
      background-repeat: no-repeat; background-size: cover; background-position: center; background-attachment: fixed; font-family: Arial, sans-serif; text-align: center;
    }
    p {
      color: #C908C1; <!-- color para párrafos -->
    }
    
    h2{
     
      color: #C908C1; <!-- color para encabezados h2 -->

    }
    </style>

</head>
<body class="bg-dark text-light text-center"> <!-- clases de Bootstrap para estilo -->
 <div>
    <img src="https://i.pinimg.com/originals/1e/c2/50/1ec2506e6843eb55d8c21059232333b5.gif" width="280rem" height="190rem"> <!-- GIF decorativo en la página -->
  </div>
    <div class="container py-4">
        <h1 class="mb-4">Control de Motor DC</h1> <!-- encabezado principal -->

        <label for="velocidad" class="form-label">Velocidad del Motor (%)</label> <!-- etiqueta para el slider -->
        <input type="range" class="form-range" min="-100" max="100" value="0" id="velocidad"> <!-- slider que va de -100 a 100 -->

        <p class="mt-3">Velocidad actual: <span id="valor">0</span>%</p> <!-- texto que muestra el valor actual del slider -->

        <canvas id="indicador" width="200" height="200"></canvas> <!-- canvas donde Chart.js dibuja el medidor -->
    </div>

<script>
const slider = document.getElementById("velocidad"); // obtiene referencia al control deslizante (slider)
const valor = document.getElementById("valor");      // obtiene referencia al span donde se mostrará el valor
const ctx = document.getElementById("indicador").getContext("2d"); // contexto 2D del canvas para Chart.js

let chart = new Chart(ctx, { // crea un gráfico tipo doughnut que sirve como medidor
    type: 'doughnut', // tipo de gráfico
    data: {
        labels: ["Velocidad", "Restante"], // etiquetas del dataset
        datasets: [{
            data: [0, 100], // valores iniciales: 0% velocidad, 100% restante
            backgroundColor: ["#0d6efd", "#343a40"], // colores del gráfico
            borderWidth: 1
        }]
    },
    options: {
        circumference: 180, // mostrar media circunferencia como indicador
        rotation: 270,      // rotación para posicionar el medidor
        cutout: "70%",      // hueco central (estética)
        plugins: {legend: {display: false}} // oculta la leyenda
    }
});

slider.addEventListener("input", () => { // evento que se dispara cuando el usuario mueve el slider
    let val = parseInt(slider.value); // obtiene el valor actual del slider y lo convierte a entero
    valor.textContent = val; // actualiza el texto en la página con el valor actual

    fetch(`/set?valor=${val}`); // envía una petición GET al servidor de la Pico con el valor (parámetro 'valor')
    
    chart.data.datasets[0].data[0] = Math.abs(val); // actualiza el gráfico con la magnitud de la velocidad
    chart.data.datasets[0].data[1] = 100 - Math.abs(val); // actualiza la parte restante del medidor
    chart.update(); // redibuja el gráfico con los nuevos valores
});
</script>
</body>
</html>
"""  # string que contiene todo el HTML que la Pico servirá al cliente

# ---------------------------
# Servidor Web
# ---------------------------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1] # obtiene la tupla de direcciones para bind en todas las interfaces puerto 80
s = socket.socket()                              # crea el socket TCP
s.bind(addr)                                     # enlaza el socket a la dirección/puerto
s.listen(1)                                      # empieza a escuchar, con cola de 1 conexión
print("Servidor corriendo en http://", wlan.ifconfig()[0]) # muestra la IP asignada por el router

while True:
    cl, addr = s.accept()                        # espera (bloqueante) hasta que un cliente se conecte
    print("Cliente conectado:", addr)            # imprime la IP del cliente que se conectó
    request = cl.recv(1024).decode()             # lee hasta 1024 bytes de la petición HTTP y la decodifica a texto

    if "/set?valor=" in request:                 # si la petición contiene el patrón /set?valor= entonces es cambio de velocidad
        try:
            val_str = request.split("/set?valor=")[1].split(" ")[0] # extrae el número que viene después de /set?valor=
            val = int(val_str)                   # convierte la cadena extraída a entero
            print("Velocidad recibida:", val)    # muestra en consola el valor recibido
            set_motor(val)                       # llama a la función que aplica PWM según el valor
        except:                                  # captura cualquier error en el parsing/conversión
            pass                                 # en caso de error lo ignoramos (podrías registrar el error aquí)

    cl.send("HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n") # envía cabecera HTTP básica con estado 200 y tipo HTML
    cl.send(html)                                 # envía el contenido HTML completo al cliente
    cl.close()                                    # cierra la conexión con el cliente
