import streamlit as st
import pandas as pd
from analysis import load_data, judge_result
def recommend_hunters(df, map_name):
    result_score_map = {
        "hunter_win": 1,
        "draw": 0.5,
        "hunter_lose": 0
    }

    df = df.copy()
    df["match_result"] = df["result"].apply(judge_result)

    # 筛选地图
    sub = df[df["map"] == map_name]

    # 统计每个屠夫的得分
    records = []
    for _, row in sub.iterrows():
        result_score = result_score_map.get(row["match_result"], None)
        if result_score is None:
            continue
        records.append({
            "hunter": row["picks_hunter"],
            "score": result_score
        })

    if not records:
        return pd.DataFrame()

    hunter_df = pd.DataFrame(records)
    stats = (
        hunter_df
        .groupby("hunter")["score"]
        .agg(["count", "mean"])
        .rename(columns={"count": "场次", "mean": "平均得分"})
        .sort_values(by="平均得分", ascending=False)
    )

    return stats.reset_index()
def show_hunter_recommend_page():
    st.title("屠夫推荐系统")

    df = load_data()


    if df.empty:
        st.error("数据加载失败或为空。")
        return

    maps = sorted(df["map"].dropna().unique())
    selected_map = st.selectbox("选择地图", maps)
    if "map" not in df.columns:
        st.error("数据中找不到 'map' 字段，请确认列名是否正确。")
        st.stop()

    if st.button("生成推荐"):
        stats = recommend_hunters(df, selected_map)

        if stats.empty:
            st.warning("没有符合条件的数据。")
        else:
            st.success(f"共找到 {len(stats)} 名屠夫的记录")
            st.dataframe(stats, use_container_width=True)
            st.bar_chart(data=stats.set_index("hunter")["平均得分"].head(10))
