import requests 
import pandas as pd 
from datetime import date 
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# ---------------- API ESPN ---------------------- #
url = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/statistics/byathlete?region=us&lang=en&contentorigin=espn&isqualified=true&page=1&limit=316&sort=offensive.avgPoints%3Adesc"

params = {
    "region": "us",
    "lang": "en",
    "contentorigin": "espn",
    "isqualified": "true",
    "page": "1",
    "limit": "316",
    "sort": "offensive.avgPoints:desc"
}

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

# ---------------- DATOS RECOPILADOS ------------------ #

players_dim = []
stats_fact = []

for item in data["athletes"]:
    athlete = item["athlete"]

    # -- DIM_PLAYER -- #
    players_dim.append({
        "player_id": athlete["id"],
        "first_name": athlete["firstName"],
        "last_name": athlete["lastName"],
        "display_name": athlete["displayName"],
        "age": athlete["age"],
        "position": athlete["position"]["abbreviation"],
        "team_id": athlete["teamId"],
        "team_name": athlete["teamName"],
        "team_short_name": athlete["teamShortName"],
        "status": athlete["status"]["name"],
        "debut_year": athlete.get("debutYear")
    })

    # -- FACT SNAPSHOT -- #
    categories = {c["name"]: c["values"] for c in item["categories"]}

    general = categories.get("general", [])
    offensive = categories.get("offensive", [])
    defensive = categories.get("defensive", [])

    stats_fact.append({
        "player_id": athlete["id"],
        "season": "2025-2026",
        "snapshot_date": date.today(),

        # General
        "games_played": general[0] if len(general) > 0 else None,
        "minutes_avg": general[1] if len(general) > 1 else None,
        "fouls_avg": general[2] if len(general) > 2 else None,
        "flagrantfouls_avg": general[3] if len(general) > 3 else None,
        "technicalfouls_avg": general[4] if len(general) > 4 else None,
        "ejections_avg": general[5] if len(general) > 5 else None,
        "dd2": general[6] if len(general) > 6 else None,
        "td3": general[7] if len(general) > 7 else None,
        "total_minutes": general[8] if len(general) > 8 else None,
        "total_rebounds": general[9] if len(general) > 9 else None,
        "total_fouls": general[10] if len(general) > 10 else None,
        "rebounds_avg": general[11] if len(general) > 11 else None,

        # Offensive
        "points_avg": offensive[0] if len(offensive) > 0 else None,
        "fg_made_avg": offensive[1] if len(offensive) > 1 else None,
        "fg_attempt_avg": offensive[2] if len(offensive) > 2 else None,
        "fg_pct": offensive[3] if len(offensive) > 3 else None,
        "three_pt_made_avg": offensive[4] if len(offensive) > 4 else None,
        "three_pt_attempt_avg": offensive[5] if len(offensive) > 5 else None,
        "three_pt_pct": offensive[6] if len(offensive) > 6 else None,
        "ft_made_avg": offensive[7] if len(offensive) > 7 else None,
        "ft_attempt_avg": offensive[8] if len(offensive) > 8 else None,
        "ft_pct": offensive[9] if len(offensive) > 9 else None,
        "assists_avg":offensive[10] if len(offensive) > 10 else None,
        "turnovers_avg": offensive[11] if len(offensive) > 11 else None,
        "total_points": offensive[12] if len(offensive) > 12 else None,
        "fg_made": offensive[13] if len(offensive) > 13 else None,
        "fg_attempted": offensive[14] if len(offensive) > 14 else None,
        "three_pt_made": offensive[15] if len(offensive) > 15 else None,
        "three_pt_attempted": offensive[16] if len(offensive) > 16 else None,
        "ft_made": offensive[17] if len(offensive) > 17 else None,
        "ft_attempted": offensive[18] if len(offensive) > 18 else None,
        "total_assists": offensive[19] if len(offensive) > 19 else None,
        "total_turnovers": offensive[20] if len(offensive) > 20 else None,
        

        # Defensive
        "steals_avg": defensive[0] if len(defensive) > 0 else None,
        "blocks_avg": defensive[1] if len(defensive) > 1 else None,
        "total_steals": defensive[2] if len(defensive) > 2 else None,
        "total_blocks": defensive[3] if len(defensive) > 3 else None
    })


# ------------------- GENERAR DATAFRAMES Y CSV ------------------------------- #

df_dim_player = pd.DataFrame(players_dim).drop_duplicates("player_id")
df_fact_stats = pd.DataFrame(stats_fact)


df_dim_player.to_csv(r"..\CSV\dim_player.csv", index=False)
df_fact_stats.to_csv(r"..\CSV\fact_player_stats_snapshot.csv", index=False)


# ------------------------- INSERTAR EN BDD ---------------------------------- #

load_dotenv()

server = os.getenv("DB_SERVER")
database = os.getenv("DB_NAME")
driver = os.getenv("DB_DRIVER")


engine = create_engine(
    f"mssql+pyodbc://@{server}/{database}?driver={driver}"
)


# -- DATAFRAME DE JUGADORES A SQL -- #
df_dim_player.to_sql(
    name="staging_dim_player",
    con=engine,
    if_exists="replace",
    index=False
)

# -- MERGE SQL JUGADORES A BDD STAGING PLAYER
merge_player_query = text("""

MERGE dim_player AS target
USING staging_dim_player AS source
ON target.player_id = source.player_id

WHEN MATCHED THEN
    UPDATE SET
        first_name = source.first_name,
        last_name = source.last_name,
        display_name = source.display_name,
        age = source.age,
        position = source.position,
        team_id = source.team_id,
        team_name = source.team_name,
        team_short_name = source.team_short_name,
        status = source.status,
        debut_year = source.debut_year

WHEN NOT MATCHED THEN
    INSERT (
        player_id,
        first_name,
        last_name,
        display_name,
        age,
        position,
        team_id,
        team_name,
        team_short_name,
        status,
        debut_year
    )
    VALUES (
        source.player_id,
        source.first_name,
        source.last_name,
        source.display_name,
        source.age,
        source.position,
        source.team_id,
        source.team_name,
        source.team_short_name,
        source.status,
        source.debut_year
    );

""")

with engine.begin() as conn:
    conn.execute(merge_player_query)


# -- DATAFRAME FACT A SQL -- #

df_fact_stats.to_sql(
    name="stg_player_stats",
    con=engine,
    if_exists="replace",
    index=False
)

# -- INSERTAR FACT A BDD -- #

insert_stats_query = text("""
INSERT INTO dbo.fact_player_stats_snapshot (
    player_id,
    season,
    snapshot_date,
    games_played,
    minutes_avg,
    points_avg,
    assists_avg,
    rebounds_avg,
    fg_made_avg,
    fg_attempt_avg,
    fg_pct,
    three_pt_made_avg,
    three_pt_attempt_avg,
    three_pt_pct,
    ft_made_avg,
    ft_attempt_avg,
    ft_pct,
    steals_avg,
    blocks_avg,
    turnovers_avg,
	fouls_avg,
	flagrantfouls_avg,
	technicalfouls_avg,
	ejections_avg,
	dd2,
	td3,
	total_minutes,
	total_rebounds,
	total_fouls,
	total_points,
	fg_made,
	fg_attempted,
	three_pt_made,
	three_pt_attempted,
	ft_made,
	ft_attempted,
	total_assists,
	total_turnovers,
	total_steals,
	total_blocks
)

SELECT
    s.player_id,
    s.season,
    s.snapshot_date,
    s.games_played,
    s.minutes_avg,
    s.points_avg,
    s.assists_avg,
    s.rebounds_avg,
    s.fg_made_avg,
    s.fg_attempt_avg,
    s.fg_pct,
    s.three_pt_made_avg,
    s.three_pt_attempt_avg,
    s.three_pt_pct,
    s.ft_made_avg,
    s.ft_attempt_avg,
    s.ft_pct,
    s.steals_avg,
    s.blocks_avg,
    s.turnovers_avg,
	s.fouls_avg,
	s.flagrantfouls_avg,
	s.technicalfouls_avg,
	s.ejections_avg,
	s.dd2,
	s.td3,
	s.total_minutes,
	s.total_rebounds,
	s.total_fouls,
	s.total_points,
	s.fg_made,
	s.fg_attempted,
	s.three_pt_made,
	s.three_pt_attempted,
	s.ft_made,
	s.ft_attempted,
	s.total_assists,
	s.total_turnovers,
	s.total_steals,
	s.total_blocks

FROM dbo.stg_player_stats s
""")

with engine.begin() as conn:
    conn.execute(insert_stats_query)