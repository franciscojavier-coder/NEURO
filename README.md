# Neurona Visual

Aplicación web local en Python para enseñar a una red neuronal a reconocer
gestos, números u objetos usando la cámara. Toda la aplicación —servidor,
interfaz y modelo— está contenida en `app.py` y no necesita paquetes externos.

## Ejecutar en Windows, Linux o macOS

Abre una terminal dentro de esta carpeta y ejecuta:

```bash
python app.py
```

En algunas distribuciones Linux el comando de Python se llama `python3`:

```bash
python3 app.py
```

El servidor abrirá automáticamente <http://127.0.0.1:8000>. Permite el uso de
la cámara cuando el navegador lo solicite. Para detenerlo, presiona `Ctrl+C`.

No abras `static/index.html` directamente: una dirección que comienza con
`file:///` no tiene conexión con Python y no puede entrenar el modelo.

## Cómo enseñarle

- Escribe una etiqueta como `1`, `2`, `mano abierta`, `taza` o `teléfono`.
- Muestra el ejemplo y pulsa **Guardar ejemplo** entre 10 y 20 veces, variando
  un poco la posición y el ángulo.
- Repite el proceso con al menos dos etiquetas.
- Pulsa **Entrenar neurona**.

La clasificación funciona mejor si el fondo y la iluminación se mantienen
parecidos. Este prototipo es educativo: aprende únicamente de los ejemplos de
la sesión y los pierde al detener el servidor.
