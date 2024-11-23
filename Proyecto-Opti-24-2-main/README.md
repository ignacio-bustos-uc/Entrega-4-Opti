# Proyecto-Opti-24-2

# Archivos CSV Requeridos

## 1. comunas.csv
**Columnas:**
- id_comuna
- id_provincia
- nombre_provincia
- nombre_comuna

**Propósito:**  
Define el conjunto de comunas **C** y sus atributos.

---

## 2. fuentes_existentes_por_comuna.csv
**Columnas:**
- id_fuente
- id_comuna

**Propósito:**  
Define las fuentes de agua **E** y asigna cada fuente a una comuna **C**. Estos datos se utilizarán para construir el parámetro **𝛿ᵉ𝚌**.

---

## 3. generadores.csv
**Columnas:**
- id_generador
- tipo_generador
- capacidad (kW)

**Propósito:**  
Define los tipos de generadores **G** y sus capacidades. Estos datos se utilizarán para definir **𝐽ᵍˢ** y **G**.

---

## 4. fuentes_demandas.csv
**Columnas:**
- id_fuente
- demanda_agua (litros)

**Propósito:**  
Proporciona la demanda de agua **𝐻ₑ** para cada fuente de agua **e**.

---

## 5. fuentes_energia_por_litro.csv
**Columnas:**
- id_fuente
- energia_por_litro (kW/litro)

**Propósito:**  
Proporciona la energía requerida por litro de agua **𝐶ₑ** en cada fuente de agua **e**.

---

## 6. ubicaciones.csv
**Columnas:**
- id_ubicacion
- id_comuna

**Propósito:**  
Define las posibles ubicaciones para la instalación de generadores **S** y asigna cada ubicación a una comuna **C**. Estos datos se utilizarán para construir el parámetro **𝜖ₛ𝚌**.

---

## 7. max_generadores_por_tipo_por_comuna.csv
**Columnas:**
- id_generador
- id_comuna
- max_generators

**Propósito:**  
Proporciona el número máximo de generadores del tipo **g** que pueden ser instalados en la comuna **c**, definiendo **𝑍₉𝚌**.

---

## 8. generator_capacidades_por_ubicacion.csv
**Columnas:**
- id_generador
- id_ubicacion
- capacidad (kW)

**Propósito:**  
Si las capacidades de los generadores varían según la ubicación **s**, este archivo proporciona **𝐽ᵍˢ** directamente. Si las capacidades son constantes por tipo de generador, se pueden utilizar las capacidades de generadores.csv y asumir que son las mismas para todas las ubicaciones.



## Conjuntos:

- **E**: Fuentes de agua, desde `fuentes_existentes_por_comuna.csv`.
- **G**: Tipos de generadores, desde `generadores.csv`.
- **S**: Ubicaciones de instalación de generadores, desde `ubicaciones.csv`.
- **C**: Comunas, desde `comunas.csv`.

## Parámetros:

- **Hₑ**: Demanda de agua por fuente, desde `fuentes_demandas.csv`.
- **Cₑ**: Energía requerida por litro por fuente, desde `fuentes_energia_por_litro.csv`.
- **𝛿ₑ𝚌**: Asignación fuente-comuna, desde `fuentes_existentes_por_comuna.csv`.
- **𝜖ₛ𝚌**: Asignación ubicación-comuna, desde `ubicaciones.csv`.
- **𝐽ᵍˢ**: Capacidades de los generadores, desde `generadores.csv` (y opcionalmente desde `generator_capacidades_por_ubicacion.csv` si las capacidades varían por ubicación).
- **𝑍₉𝚌**: Máximo de generadores por tipo y por comuna, desde `max_generadores_por_tipo_por_comuna.csv`.
- **Pₐₑ**: Presupuesto por comuna. ``presupuesto_por_comuna.csv``
