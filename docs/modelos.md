# Modelos del software

Diagramas en Mermaid (se ven directamente en GitHub/VS Code; para exportar a imagen: <https://mermaid.live>).
Los nombres coinciden con el código de la versión `v2-cambio`.

## 1. Contexto

```mermaid
flowchart LR
    Escritor(["Escritor/a del colectivo"])
    Lector(["Lector/a del festival"])
    Archivos[("Archivos de historia<br/>historias/*.json")]
    Motor["Motor de historias<br/>(python -m motor)"]

    Escritor -- "escribe y edita" --> Archivos
    Escritor -- "--validar ruta" --> Motor
    Motor -- "lista de errores con causa y ubicación" --> Escritor
    Archivos -- "se cargan y validan" --> Motor
    Lector -- "elige opciones / deshacer / reiniciar" --> Motor
    Motor -- "escena, opciones habilitadas, «FIN»" --> Lector
```

## 2. Casos de uso

```mermaid
flowchart LR
    Escritor(["Escritor/a"])
    Lector(["Lector/a"])
    subgraph Motor de historias
        CU1(["Cargar historia"])
        CU2(["Validar historia"])
        CU3(["Leer escena"])
        CU4(["Elegir opción"])
        CU5(["Deshacer última elección<br/>(RF17, cambio)"])
        CU6(["Reiniciar partida"])
    end
    Escritor --- CU2
    Lector --- CU1
    Lector --- CU3
    Lector --- CU4
    Lector --- CU5
    Lector --- CU6
    CU1 -. "«include»" .-> CU2
    CU4 -. "«include»" .-> CU3
```

| Caso de uso | Actor | RF |
|---|---|---|
| Cargar historia | Lector | RF01, RF02 |
| Validar historia | Escritor (y Cargar, por inclusión) | RF10–RF15 |
| Leer escena | Lector | RF03, RF04, RF08, RF16 |
| Elegir opción | Lector | RF05, RF06, RF07 |
| Deshacer última elección | Lector | RF17 |
| Reiniciar partida | Lector | RF09 |

## 3. Clases del dominio

```mermaid
classDiagram
    direction LR
    class Historia {
        +titulo: str
        +inicio: str
        +variables: Mapping~str,bool~
        +escenas: tuple~Escena~
        +escena(id) Escena
        +tiene_escena(id) bool
    }
    class Escena {
        +id: str
        +texto: str
        +final: bool
        +opciones: tuple~Opcion~
        +buscar_opcion(id) Opcion
    }
    class Opcion {
        +id: str
        +texto: str
        +destino: str
        +condiciones: Mapping~str,bool~
        +efectos: Mapping~str,bool~
        +esta_habilitada(variables) bool
    }
    class Sesion {
        -_id_escena: str
        -_variables: dict~str,bool~
        -_anterior: tuple~str,dict~ | None
        +escena_actual: Escena
        +variables: dict~str,bool~
        +es_final: bool
        +esta_bloqueada: bool
        +puede_deshacer: bool
        +opciones_habilitadas() list~Opcion~
        +elegir(id_opcion) ResultadoAccion
        +deshacer() ResultadoAccion
        +reiniciar()
    }
    class ResultadoAccion {
        +codigo: str
        +mensaje: str
        +ok: bool
    }
    class ErrorContenido {
        +codigo: str
        +mensaje: str
        +ubicacion: str
    }
    class HistoriaInvalida {
        +errores: list~ErrorContenido~
    }
    Historia "1" *-- "1..*" Escena
    Escena "1" *-- "0..*" Opcion
    Opcion ..> Escena : destino (por id)
    Sesion --> "1" Historia : juega (solo lectura)
    Sesion ..> ResultadoAccion : devuelve
    HistoriaInvalida "1" o-- "1..*" ErrorContenido
```

`Historia`, `Escena` y `Opcion` son inmutables (dataclasses `frozen`, mapas de solo lectura). `_anterior` es la instantánea de un nivel agregada por el cambio.

## 4. Secuencia «elegir una opción»

```mermaid
sequenceDiagram
    actor Lector
    participant C as Consola (cli.py)
    participant S as Sesion
    participant E as Escena actual
    participant O as Opcion

    Lector->>C: escribe "2" o "investigar"
    C->>S: opciones_habilitadas() (si es número)
    C->>S: elegir(id_opcion)
    alt la escena es final
        S-->>C: ResultadoAccion(PARTIDA_FINALIZADA)
    else
        S->>E: buscar_opcion(id_opcion)
        E-->>S: Opcion o None
        alt no existe
            S-->>C: ResultadoAccion(OPCION_INEXISTENTE)
        else existe
            S->>O: esta_habilitada(variables)
            alt condiciones no cumplidas
                S-->>C: ResultadoAccion(OPCION_NO_HABILITADA)
            else habilitada
                S->>S: nuevas = copia(variables) + efectos
                S->>S: _anterior = (escena, copia(variables))  [cambio RF17]
                S->>S: escena = destino, variables = nuevas
                S-->>C: ResultadoAccion(OK)
            end
        end
    end
    C-->>Lector: mensaje de rechazo (estado intacto) o nueva escena
```

Una entrada rechazada no toca `escena`, `variables` ni `_anterior`.

## 5. Estados de una sesión

```mermaid
stateDiagram-v2
    [*] --> Validando : cargar archivo
    Validando --> CargaRechazada : errores > 0
    CargaRechazada --> [*] : lista de errores, código 2
    Validando --> EnCurso : 0 errores / escena = inicio

    EnCurso --> EnCurso : elegir [habilitada y destino con opciones habilitadas]
    EnCurso --> Finalizada : elegir [habilitada y destino final]
    EnCurso --> Bloqueada : elegir [habilitada y destino no final sin opciones habilitadas]
    EnCurso --> EnCurso : elegir [inexistente o no habilitada] / sin cambios
    EnCurso --> EnCurso : deshacer [puede_deshacer]
    EnCurso --> EnCurso : reiniciar

    Finalizada --> EnCurso : deshacer [puede_deshacer]
    Finalizada --> EnCurso : reiniciar
    Finalizada --> Finalizada : elegir / PARTIDA_FINALIZADA

    Bloqueada --> EnCurso : deshacer [puede_deshacer]
    Bloqueada --> EnCurso : reiniciar

    EnCurso --> [*] : salir
    Finalizada --> [*] : salir
    Bloqueada --> [*] : salir
```

Deshacer siempre lleva a `EnCurso`: la escena restaurada tenía al menos una opción habilitada (la que se eligió) con las variables restauradas. Tras `deshacer` o `reiniciar`, `puede_deshacer` es falso.
