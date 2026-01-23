import requests 
import pandas as pd 
from datetime import date 
import json

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

## print(json.dumps(data, indent=2)) Para ver los datos obtenidos


################################
###---------- ETL ---------- ###
################################

players_dim = []
stats_fact = []

for item in data["athletes"]:
    athlete = item["athlete"]

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

        # Offensive
        "points_avg": offensive[0] if len(offensive) > 0 else None,
        "assists_avg": offensive[1] if len(offensive) > 1 else None,
        "rebounds_avg": offensive[2] if len(offensive) > 2 else None,
        "fg_pct": offensive[3] if len(offensive) > 3 else None,
        "three_pt_made_avg": offensive[4] if len(offensive) > 4 else None,
        "three_pt_attempt_avg": offensive[5] if len(offensive) > 5 else None,
        "three_pt_pct": offensive[6] if len(offensive) > 6 else None,
        "ft_made_avg": offensive[7] if len(offensive) > 7 else None,
        "ft_attempt_avg": offensive[8] if len(offensive) > 8 else None,
        "ft_pct": offensive[9] if len(offensive) > 9 else None,

        # Defensive
        "steals_avg": defensive[0] if len(defensive) > 0 else None,
        "blocks_avg": defensive[1] if len(defensive) > 1 else None
    })

####################################
# ---------- DataFrames ---------- #
####################################

df_dim_player = pd.DataFrame(players_dim).drop_duplicates("player_id")
df_fact_stats = pd.DataFrame(stats_fact)


##################################
# ------- Exportar a CSV ------- #
##################################

df_dim_player.to_csv(r"..\CSV\dim_player.csv", index=False)
df_fact_stats.to_csv(r"..\CSV\fact_player_stats_snapshot.csv", index=False)