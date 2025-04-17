import pandas as pd
from collections import defaultdict, Counter
import ast
import os


def load_data(file_name="bp_data.xlsx"):
    # 始终从 main.py 的目录开始找文件
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, file_name)

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        print(f"Error loading the file: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of failure

    # Ensure correct parsing of picks and bans (from strings to lists)
    for col in ['picks_survivor', 'bans_survivor', 'bans_hunter']:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    return df
def judge_result(result_str):
    try:
        a, b = map(int, result_str.strip().split(":"))
        if b > a:
            return "hunter_win"
        elif a == b:
            return "draw"
        else:
            return "hunter_lose"
    except ValueError:
        print(f"Invalid result format: {result_str}")
        return "invalid"
def hunter_winrate_analysis(df):
    df["match_result"] = df["result"].apply(judge_result)
    hunter_stats = defaultdict(lambda: {"win": 0, "lose": 0, "draw": 0})

    for _, row in df.iterrows():
        hunter = row["picks_hunter"]  # Corrected to match 'picks_hunter'
        result = row["match_result"]
        if result in ["hunter_win", "hunter_lose", "draw"]:
            hunter_stats[hunter][result.split("_")[-1]] += 1

    hunter_winrate = {
        hunter: {
            **counts,
            "winrate": round(100 * counts["win"] / (counts["win"] + counts["lose"] + counts["draw"]), 2) if counts[
                                                                                                                "win"] +
                                                                                                            counts[
                                                                                                                "lose"] +
                                                                                                            counts[
                                                                                                                "draw"] > 0 else 0
        }
        for hunter, counts in hunter_stats.items()
    }

    return pd.DataFrame.from_dict(hunter_winrate, orient="index").sort_values(by="winrate", ascending=False)
def survivor_impact_analysis(df):
    df["match_result"] = df["result"].apply(judge_result)
    survivor_impact = defaultdict(lambda: {"win": 0, "lose": 0, "draw": 0})

    for _, row in df.iterrows():
        survivors = row["picks_survivor"]  # Corrected to match 'picks_survivor'
        result = row["match_result"]
        for s in survivors:
            if result == "hunter_win":
                survivor_impact[s]["lose"] += 1
            elif result == "hunter_lose":
                survivor_impact[s]["win"] += 1
            elif result == "draw":
                survivor_impact[s]["draw"] += 1

    df_survivor_impact = pd.DataFrame.from_dict(survivor_impact, orient="index")
    df_survivor_impact["total"] = df_survivor_impact.sum(axis=1)
    df_survivor_impact["winrate"] = round(df_survivor_impact["win"] / df_survivor_impact["total"] * 100, 2) if \
    df_survivor_impact["total"].sum() > 0 else 0

    return df_survivor_impact.sort_values(by="total", ascending=False)
def ban_pick_heatmap_analysis(df):
    all_picks_survivor = []
    all_picks_hunter = []
    for _, row in df.iterrows():
        all_picks_survivor.extend(row['picks_survivor'])
        all_picks_hunter.append(row['picks_hunter'])

    pick_counts_survivor = dict(Counter(all_picks_survivor))
    pick_counts_hunter = dict(Counter(all_picks_hunter))

    all_bans_survivor = []
    all_bans_hunter = []
    for _, row in df.iterrows():
        all_bans_survivor.extend(row['bans_survivor'])
        all_bans_hunter.extend(row['bans_hunter'])

    ban_counts_survivor = dict(Counter(all_bans_survivor))
    ban_counts_hunter = dict(Counter(all_bans_hunter))

    return {
        "pick_counts_survivor": pick_counts_survivor,
        "pick_counts_hunter": pick_counts_hunter,
        "ban_counts_survivor": ban_counts_survivor,
        "ban_counts_hunter": ban_counts_hunter
    }
def survivor_combo_analysis(df, min_games=3):
    df["match_result"] = df["result"].apply(judge_result)
    combo_stats = defaultdict(lambda: {"win": 0, "draw": 0, "lose": 0})

    # Debug: Check the structure of "picks_survivor"
    print("Inspecting picks_survivor and result")

    for _, row in df.iterrows():
        result = row["match_result"]
        combo = frozenset(row["picks_survivor"])

        # Debug: Ensure 'picks_survivor' is a list-like object
        print(f"combo: {combo}, result: {result}")

        if result == "hunter_win":
            combo_stats[combo]["lose"] += 1
        elif result == "hunter_lose":
            combo_stats[combo]["win"] += 1
        elif result == "draw":
            combo_stats[combo]["draw"] += 1

    result_df = []
    for combo, counts in combo_stats.items():
        total = sum(counts.values())

        # Debug: Check the total count and winrate calculation
        print(f"combo: {combo}, win: {counts['win']}, draw: {counts['draw']}, lose: {counts['lose']}, total: {total}")

        if total >= min_games:
            winrate = round(100 * counts["win"] / total, 2) if total > 0 else 0
            result_df.append({
                "combo": ", ".join(combo),
                "win": counts["win"],
                "draw": counts["draw"],
                "lose": counts["lose"],
                "total": total,
                "winrate": winrate,
            })

    return pd.DataFrame(result_df).sort_values(by="winrate", ascending=False)
def ban_survivor_effect(df, min_games=3):
    df["match_result"] = df["result"].apply(judge_result)
    ban_stats = defaultdict(lambda: {"ban_win": 0, "ban_total": 0})
    for _, row in df.iterrows():
        banned = row["bans_survivor"]
        result = row["match_result"]
        for s in banned:
            ban_stats[s]["ban_total"] += 1
            if result == "hunter_win":
                ban_stats[s]["ban_win"] += 1

    result_df = []
    for name, v in ban_stats.items():
        if v["ban_total"] >= min_games:
            winrate = round(100 * v["ban_win"] / v["ban_total"], 2) if v["ban_total"] > 0 else 0
            result_df.append({
                "survivor": name,
                "ban_times": v["ban_total"],
                "winrate_when_banned": winrate
            })

    return pd.DataFrame(result_df).sort_values(by="winrate_when_banned", ascending=False)
def hunter_winrate_by_map(df):
    df["match_result"] = df["result"].apply(judge_result)
    stats = defaultdict(lambda: {"win": 0, "lose": 0, "draw": 0})
    for _, row in df.iterrows():
        m = row["map"]
        result = row["match_result"]
        if result == "hunter_win":
            stats[m]["win"] += 1
        elif result == "hunter_lose":
            stats[m]["lose"] += 1
        elif result == "draw":
            stats[m]["draw"] += 1

    df_map = []
    for map_name, counts in stats.items():
        total = sum(counts.values())
        winrate = round(100 * counts["win"] / total, 2) if total > 0 else 0
        df_map.append({
            "map": map_name,
            "win": counts["win"],
            "lose": counts["lose"],
            "draw": counts["draw"],
            "winrate": winrate
        })

    return pd.DataFrame(df_map).sort_values(by="winrate", ascending=False)
def survivor_winrate_by_map(df):
    df["match_result"] = df["result"].apply(judge_result)
    stats = defaultdict(lambda: {"win": 0, "lose": 0, "draw": 0})

    # 计算每个求生者在不同地图上的胜率
    for _, row in df.iterrows():
        map_name = row["map"]  # 地图
        survivors = row["picks_survivor"]  # 求生者角色
        result = row["match_result"]  # 比赛结果

        # 确保每个求生者角色单独作为键
        for survivor in survivors:
            # 确保 survivor 是一个不可变类型，例如字符串
            if isinstance(survivor, list):
                survivor = tuple(survivor)  # 将列表转换为元组（不可变）

            if result == "hunter_win":
                stats[(map_name, survivor)]["lose"] += 1
            elif result == "hunter_lose":
                stats[(map_name, survivor)]["win"] += 1
            elif result == "draw":
                stats[(map_name, survivor)]["draw"] += 1

    # 计算每个求生者在不同地图上的胜率
    df_map = []
    for (map_name, survivor), counts in stats.items():
        total = sum(counts.values())
        winrate = round(100 * counts["win"] / total, 2) if total > 0 else 0
        df_map.append({
            "map": map_name,
            "survivor": survivor,
            "winrate": winrate,
            "win": counts["win"],
            "lose": counts["lose"],
            "draw": counts["draw"]
        })

    return pd.DataFrame(df_map).sort_values(by="winrate", ascending=False)
def all_analysis(file_path=None):
    if file_path is None:
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir,"bp_data.xlsx")

    df = load_data(file_path)
    if df.empty:
        return {}

    df["match_result"] = df["result"].apply(judge_result)

    return {
        "hunter_winrate": hunter_winrate_analysis(df),
        "survivor_impact": survivor_impact_analysis(df),
        "ban_pick_stats": ban_pick_heatmap_analysis(df),
        "survivor_combos": survivor_combo_analysis(df),
        "ban_effect": ban_survivor_effect(df),
        "map_winrate": hunter_winrate_by_map(df)
    }

