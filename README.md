# Control de Motor DC con Raspberry Pi Pico W

Este proyecto implementa un sistema de **control de velocidad de un motor de corriente continua** utilizando una **Raspberry Pi Pico W** y un **módulo puente H L9110S**.  
La Pico W actúa como **servidor web**, hospedando una página accesible desde cualquier dispositivo móvil o PC conectado a la misma red Wi-Fi.  
Desde la página se puede **ajustar la velocidad y dirección del motor en tiempo real** mediante un control deslizante (slider) y visualizarla en un **indicador gráfico (medidor con Chart.js)**.


## Materiales necesarios
- 1x Raspberry Pi Pico W  
- 1x Módulo puente H L9110S  
- 1x Motor DC (dos cables)  
- Fuente de alimentación externa de **5V** (ej. batería, powerbank o adaptador)  
- Cables jumper  


## Conexiones
Entre la Pico W y el L9110S (canal A):
- **GPIO15 (Pico) → A-1A (L9110S)**  
- **GPIO14 (Pico) → A-1B (L9110S)**  
- **GND (Pico) → GND (L9110S)**  
- **5V fuente externa → VCC (L9110S)**  
- **GND fuente externa → GND Pico y GND L9110S (tierra común)**  

Motor:
- Conectar el motor a **OUT A-1A y OUT A-1B** del módulo L9110S.

Importante: No alimentar el L9110S desde el pin 3.3V de la Pico. Usa 5V externos para dar suficiente corriente al motor.

---

## Funcionamiento
1. La Pico W se conecta a la red Wi-Fi indicada en el código (`SSID` y `PASSWORD`).  
2. Inicia un servidor web en el puerto 80.  
3. Al ingresar la IP de la Pico en un navegador (por ejemplo: `http://192.168.1.50`), se carga una página con:
   - Un **slider** para ajustar la velocidad en rango `-100` a `100`:  
     - Valores positivos = motor gira hacia adelante.  
     - Valores negativos = motor gira hacia atrás.  
     - Valor `0` = motor detenido.  
   - Un medidor gráfico (doughnut) que muestra visualmente la magnitud de la velocidad.  

4. Los cambios en el slider envían solicitudes al servidor (`/set?valor=X`), que ajusta el PWM en los pines del L9110S.  
5. El motor responde en tiempo real al cambio de velocidad y dirección.  

---

## Interfaz Web
- Diseño responsivo** usando **Bootstrap** (compatible con móviles y PC).  
- Control deslizante (slider)** para cambiar la velocidad.  
- Indicador gráfico** creado con **Chart.js**.  
- Fondo personalizado e imágenes decorativas.  

## Ejemplo de vista en el navegador:  
- Control del motor con slider.  
- Visualización inmediata de velocidad actual.  
- Indicador circular mostrando porcentaje.  

---

## Archivos principales
- `main.py` → Código principal en MicroPython para la Pico W (servidor web + control motor).  
- Página HTML embebida en `main.py` con:
  - Bootstrap para estilos.  
  - Chart.js para el medidor de velocidad.  
  - JavaScript para enviar datos al servidor y actualizar la interfaz.  

---

## Instalación y uso
1. Instalar **MicroPython** en la Raspberry Pi Pico W.  
2. Abrir Thonny IDE y cargar `main.py` en la Pico.  
3. Modificar en el código tus credenciales Wi-Fi:
   ```python
   SSID = "Tu-SSID"
   PASSWORD = "Tu-Contraseña"

