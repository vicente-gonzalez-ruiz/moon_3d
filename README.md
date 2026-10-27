# Mathematical Foundation of the Image Alignment Pipeline

When capturing two photographs of the Moon at different times of the day (e.g., at dawn and dusk), the two images will differ in **translation** ($\Delta x, \Delta y$), **rotation** ($\Delta \theta$), and **scale** ($s$). 

To align the images before generating a 3D stereo pair, we apply a two-stage method based on **Fourier Phase Correlation** and the **Log-Polar Transform** (a variant of the Fourier-Mellin Transform).

---

## 1. Stage 1: Translational Alignment via Phase Correlation

Before computing rotation and scale, we must first estimate and remove any spatial shift $(\Delta x, \Delta y)$ so that both lunar disks share the same geometric center.

### 1.1 Cross-Power Spectrum
Given two 2D images $I_1(x, y)$ and $I_2(x,y) = I_1(x - \Delta x, y - \Delta y)$, we compute their 2D Discrete Fourier Transforms:

$$F_1(u, v) = \mathcal{F}\{I_1(x, y)\}$$

$$F_2(u, v) = \mathcal{F}\{I_2(x, y)\} = F_1(u, v) \cdot e^{-i 2\pi \left(\frac{u \Delta x}{M} + \frac{v \Delta y}{N}\right)}$$

Where $M$ and $N$ represent the image dimensions. The **Normalized Cross-Power Spectrum** $R(u, v)$ isolates the phase difference between the two signals while removing intensity variations:

$$R(u, v) = \frac{F_1(u, v) \cdot F_2^*(u, v)}{|F_1(u, v) \cdot F_2^*(u, v)|} = e^{i 2\pi \left(\frac{u \Delta x}{M} + \frac{v \Delta y}{N}\right)}$$

where $F_2^*$ denotes the complex conjugate of $F_2$.

### 1.2 Peak Detection
Applying the Inverse 2D Fourier Transform ($\mathcal{F}^{-1}$) to $R(u, v)$ yields a Dirac delta function centered exactly at the spatial shift:

$$r(x, y) = \mathcal{F}^{-1}\{R(u, v)\} = \delta(x - \Delta x, y - \Delta y)$$

The spatial shift is extracted by finding the coordinates of the maximum value in the correlation matrix:

$$(\Delta x, \Delta y) = \arg\max_{(x, y)} r(x, y)$$

Image $I_2$ is then shifted by $(-\Delta x, -\Delta y)$ to align its center with $I_1$.

---

## 2. Stage 2: Rotational and Scale Alignment via Log-Polar Transform

Once both images share a common center, rotation and scale changes are converted into simple linear translations.

### 2.1 Cartesian to Log-Polar Mapping
In Cartesian coordinates $(x, y)$, rotation by $\Delta \theta$ and scaling by $s$ are expressed as:

$$\begin{bmatrix} x' \\ y' \end{bmatrix} = s \begin{bmatrix} \cos \Delta \theta & -\sin \Delta \theta \\ \sin \Delta \theta & \cos \Delta \theta \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix}$$

By mapping the centered Cartesian grid $(x, y)$ to **Log-Polar coordinates** $(\rho, \theta)$:

$$r = \sqrt{x^2 + y^2}, \quad \theta = \arctan\left(\frac{y}{x}\right)$$

$$\rho = \ln(r)$$

The transformation converts scaling and rotation into linear offsets along the axes:

$$\theta' = \theta + \Delta \theta$$

$$\rho' = \ln(s \cdot r) = \ln(r) + \ln(s) = \rho + \ln(s)$$

* **Rotation ($\Delta \theta$):** Translates into a vertical shift along the $\theta$-axis.
* **Scale ($s$):** Translates into a horizontal shift along the $\rho$-axis.

### 2.2 Phase Correlation in Log-Polar Space
Let $P_1(\rho, \theta)$ and $P_2(\rho, \theta)$ be the log-polar representations of $I_1$ and $I_2$. Because rotation and scale are now linear translations in $(\rho, \theta)$, we apply Phase Correlation a second time:

$$R_{polar}(u_\rho, v_\theta) = \frac{\mathcal{F}\{P_1\} \cdot \mathcal{F}^*\{P_2\}}{|\mathcal{F}\{P_1\} \cdot \mathcal{F}^*\{P_2\}|}$$

Taking the inverse transform $\mathcal{F}^{-1}\{R_{polar}\}$ yields a peak at index $(d_\rho, d_\theta)$.

### 2.3 Parameter Extraction
The physical values for rotation angle $\Delta \theta$ and scale factor $s$ are computed directly from the discrete peak coordinates $(d_\rho, d_\theta)$:

1. **Rotation Angle ($\Delta \theta$):**
   $$\Delta \theta = \left( \frac{d_\theta}{N_\theta} \right) \times 360^\circ$$

   *(Adjusted to the range $[-180^\circ, 180^\circ]$ if $d_\theta > N_\theta / 2$)*

2. **Scale Factor ($s$):**
   $$s = \exp\left( \frac{d_\rho}{N_\rho} \right)$$

---

## 3. Summary of the Complete Pipeline

$$\text{Cartesian } I_1, I_2 \xrightarrow[\text{Phase Correlation}]{\text{Spatial FPC}} (\Delta x, \Delta y) \longrightarrow \text{Center Images}$$

$$\text{Centered } I_1, I_2 \xrightarrow[\text{Mapping}]{\text{Log-Polar}} P_1(\rho, \theta), P_2(\rho, \theta) \xrightarrow[\text{Phase Correlation}]{\text{Polar FPC}} (d_\rho, d_\theta)$$

$$(d_\rho, d_\theta) \longrightarrow \begin{cases} \Delta \theta = \frac{d_\theta}{N_\theta} \cdot 360^\circ \\ s = e^{d_\rho / N_\rho} \end{cases}$$

Once $(\Delta x, \Delta y)$, $\Delta \theta$, and $s$ are determined, $I_2$ is transformed back onto the grid of $I_1$ to produce a perfectly aligned image pair ready for stereo viewing.# moon_3d
# moon_3d
