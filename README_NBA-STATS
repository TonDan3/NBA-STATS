# NBA Stats 2025-26 — ETL Pipeline End-to-End

Pipeline de extracción, transformación y carga de estadísticas de la NBA desde la API pública de ESPN hacia un Data Warehouse en SQL Server, con dashboard final en Power BI.

## Stack

`Python` · `Pandas` · `SQLAlchemy` · `SQL Server` · `Power BI`

## Cómo funciona

Un scraper consume la API de ESPN y trae datos de todos los jugadores activos (~300+). Los datos se dividen en dos modelos:

- **dim_player**: datos maestros del jugador (nombre, edad, posición, equipo). Se actualiza con MERGE — si el jugador ya existe, se pisa; si es nuevo, se inserta.
- **fact_player_stats_snapshot**: estadísticas promedio por partido más totales acumulados. Cada ejecución agrega un snapshot con la fecha del día, lo que permite trackear evolución en el tiempo.

Todo fluye así: `API ESPN → Pandas → staging tables → MERGE/INSERT → tablas finales`. Las tablas staging se regeneran siempre (son transientes), las finales acumulan histórico.

El dashboard en Power BI se conecta directo al DW y permite filtrar por equipo, posición, temporada, además de visualizar distribuciones y rankings de jugadores.

## Archivos clave

```
Scripts/Scraper.py          # Pipeline completo (extracción → staging → carga final)
SQL/schema.sql              # Creación de base de datos, tablas e índices
CSV/dim_player.csv          # Último snapshot de jugadores (backup plano)
CSV/fact_player_stats_snapshot.csv   # Último snapshot de estadísticas
POWER BI/NBACHART2526.pbix  # Dashboard
IMG/                        # Assets para el dashboard
```

## Cómo correrlo

1. Clonar el repo
2. Configurar variables de entorno en `.env`:

```
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=NBACHART
DB_DRIVER={ODBC Driver 17 for SQL Server}
```

3. Ejecutar `SQL/schema.sql` en SQL Server Management Studio para crear la base de datos y tablas
4. Ejecutar `python Scripts/Scraper.py`

El scraper crea los CSVs automáticamente, carga las staging tables y hace el merge hacia las tablas finales.

## Disclaimer menor (pero real)

Las tablas staging terminan con tipos automaticos de `pd.to_sql`, por eso algunos campos quedan como `varchar(max)` o `float` en lugar de los tipos finales definidos manualmente en el schema. Prefiero que el schema definitivo tenga tipos controlados y que las staging sean un puente rápido — no las expongo a consumo directo.

Para produccion idealmente esto iria orquestado con algo como Airflow o Prefect, pero para un proyecto personal funciona bien con `python script.py` en el task scheduler.

## Por qué lo hice

Soy hincha de la NBA y trabajo en datos. Quería armarme un pipeline completo de principio a fin — desde conseguir los datos crudos hasta tener un dashboard para verlos — y tenerlo todo versionado en un repo. Partió como experimento y terminó siendo un proyecto entretenido que además me sirve para mostrar cómo armo un DW chico de principio a fin.

## License

MIT
