import pandas as pd
import os
from config import HUNTER_MAP,SURVIVOR_MAP,MAPS,survivor_cn_en,hunter_cn_en,maps_cn_en


def save_to_excel(data: dict, file_name="bp_data.xlsx"):
    # Define the directory for saving the file
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, file_name)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])

    df.to_excel(file_path, index=False, engine='openpyxl')
def is_duplicate_entry(match_id, team_survivor, team_hunter, bo_type, file_path="bp_data.xlsx"):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir,"bp_data.xlsx" )

    if not os.path.exists(file_path):
        return False
    df = pd.read_excel(file_path)
    df[["match_id", "team_survivor", "team_hunter", "bo_type"]] = df[["match_id", "team_survivor", "team_hunter", "bo_type"]].astype(str)
    return (
        ((df["match_id"] == str(match_id)) &
         (df["team_survivor"] == str(team_survivor)) &
         (df["team_hunter"] == str(team_hunter)) &
         (df["bo_type"] == str(bo_type)))
        .any()
    )

