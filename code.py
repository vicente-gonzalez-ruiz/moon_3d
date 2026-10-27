import numpy as np
from PIL import Image
from scipy.ndimage import warp_polar, shift, rotate

def estimar_traslacion(arr1, arr2):
    """Calcula el desplazamiento (dx, dy) entre dos imágenes usando Correlación de Fase."""
    f1 = np.fft.fft2(arr1)
    f2 = np.fft.fft2(arr2)
    cruzado = f1 * np.conj(f2)
    correlacion = np.real(np.fft.ifft2(cruzado / (np.abs(cruzado) + 1e-15)))
    
    dy, dx = np.unravel_index(np.argmax(correlacion), correlacion.shape)
    
    # Ajustar para desplazamientos negativos
    if dy > arr1.shape[0] // 2:
        dy -= arr1.shape[0]
    if dx > arr1.shape[1] // 2:
        dx -= arr1.shape[1]
        
    return dx, dy

def alinear_luna_completo(ruta_img1, ruta_img2):
    # 1. Cargar imágenes
    img1 = Image.open(ruta_img1).convert("L")
    img2 = Image.open(ruta_img2).convert("L")
    
    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)

    # 2. Paso 1: Estimar y corregir la traslación (desplazamiento de posición)
    dx, dy = estimar_traslacion(arr1, arr2)
    print(f"Desplazamiento detectado: X = {dx} px, Y = {dy} px")
    
    # Desplazar arr2 para alinearlo posicionalmente con arr1
    arr2_centrada = shift(arr2, shift=(dy, dx), mode='constant', cval=0)

    # 3. Paso 2: Transformada Log-Polar desde el centro común de la imagen
    centro = (arr1.shape[0] // 2, arr1.shape[1] // 2)
    radio_max = min(centro)

    polar1 = warp_polar(arr1, center=centro, max_radius=radio_max, scaling='log')
    polar2 = warp_polar(arr2_centrada, center=centro, max_radius=radio_max, scaling='log')

    # 4. Paso 3: Correlación de Fase en Polar para Rotación y Escala
    f1_p = np.fft.fft2(polar1)
    f2_p = np.fft.fft2(polar2)
    cruzado_p = f1_p * np.conj(f2_p)
    correlacion_p = np.real(np.fft.ifft2(cruzado_p / (np.abs(cruzado_p) + 1e-15)))

    d_angle, d_scale = np.unravel_index(np.argmax(correlacion_p), correlacion_p.shape)

    # Convertir desplazamientos a magnitud física
    angulo = (d_angle / polar1.shape[0]) * 360.0
    if angulo > 180:
        angulo -= 360

    factor_escala = np.exp(d_scale / polar1.shape[1])
    if factor_escala > 2.0:
        factor_escala = 1.0 / np.exp((polar1.shape[1] - d_scale) / polar1.shape[1])

    print(f"Ángulo de rotación detectado: {angulo:.2f}°")
    print(f"Factor de escala detectado: {factor_escala:.4f}x")

    # 5. Aplicar transformaciones completas a la imagen original a color
    img2_color = Image.open(ruta_img2)
    arr2_color = np.array(img2_color)

    # A) Traslación posicional
    if arr2_color.ndim == 3:
        arr2_corregida = np.zeros_like(arr2_color)
        for c in range(3):
            arr2_corregida[:, :, c] = shift(arr2_color[:, :, c], shift=(dy, dx))
    else:
        arr2_corregida = shift(arr2_color, shift=(dy, dx))

    # B) Escala y Rotación con Pillow
    img_resultado = Image.fromarray(arr2_corregida)
    
    if abs(factor_escala - 1.0) > 0.005:
        w, h = img_resultado.size
        img_resultado = img_resultado.resize((int(w * factor_escala), int(h * factor_escala)), Image.Resampling.BICUBIC)
    
    img_final = img_resultado.rotate(-angulo, resample=Image.Resampling.BICUBIC)
    img_final.save("luna_totalmente_alineada.jpg")

    return img_final

# Ejemplo de ejecución
# alinear_luna_completo("luna_amanecer.jpg", "luna_anochecer.jpg")