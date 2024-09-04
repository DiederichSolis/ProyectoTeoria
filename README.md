
EJECUCION DEL PROGRAMA
- Se recomienda levantar un entorno virual para evitar problemas con al instalacion
- Comandos:
  python3 -m venv myenv
  source myenv/bin/activate
  pip install graphviz

-Para el ingreso de la expresión regular 𝑟 y la cadena w se hace desde el .txt donde r y w se separan por una coma (,)
  Ejemplo:
  (b|b)*abb(a|b)*,babbaaaaa ---> r,w
  

FUNCIONAMIENTO DEL PROGRAMA:
- El proyecto presenta dos archivos .py y un .txt
- .py:
  Cuenta con el funcionamiento y logica del programa
-.txt:
  Cuenta con el ingreso  expresión regular 𝑟 junto con la cadena 𝑤

- Entrada
o Una expresión regular r.

o Una cadena w.

o Por ejemplo, se ingresa la expresión regular 𝑟 = (𝑏|𝑏) ∗ 𝑎𝑏𝑏(𝑎|𝑏) ∗ y la cadena 𝑤 =
𝑏𝑎𝑏𝑏𝑎𝑎𝑎𝑎𝑎.

o El símbolo que represente a ε será designado por el programador o programadora
(debe ser algo razonable, no una letra o un número con altas probabilidades de ser
usado en otro aspecto del proyecto).
Todos los símbolos del alfabeto son de longitud 1. El alfabeto de símbolos para la
expresión regular será conformado por todos los símbolos (no operadores) distintos
que se encuentren en la expresión regular.

- Salida
  o Por cada AF generado a partir de r:
  - Una imagen con el Grafo correspondiente para el AFN y para los AFDs
  generados (por construcción de subconjuntos y su minimización),
  mostrando el estado inicial, los estados adicionales, el estado de
  aceptación y las transiciones con sus símbolos correspondientes.
  - La simulación del AFN y de los AFDs al colocar la cadena w: el programa
  debe indicar si w ∈ L(r) con un "sí" en caso el enunciado anterior sea
  correcto, de lo contrario deberá mostrar un "no
