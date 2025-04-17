import streamlit as st
import pandas as pd
from analysis import load_data, judge_result

def recommend_survivors(df, map_name, hunter_name):
    result_score_map = {
        "hunter_lose": 1,    # 求生胜
        "draw": 0.5,
        "hunter_win": 0      # 求生负
    }

    df = df.copy()
    if df.empty:
        st.error("数据加载失败或为空。")
        return
    df["match_result"] = df["result"].apply(judge_result)

    # 筛选匹配的地图和屠夫
    sub = df[(df["map"] == map_name) & (df["picks_hunter"] == hunter_name)]

    # 展开求生者 + 添加评分
    records = []
    for _, row in sub.iterrows():
        result_score = result_score_map.get(row["match_result"], None)
        if result_score is None:
            continue
        for survivor in row["picks_survivor"]:
            records.append({
                "survivor": survivor,
                "score": result_score
            })

    if not records:
        return pd.DataFrame()

    survivor_df = pd.DataFrame(records)
    stats = (
        survivor_df
        .groupby("survivor")["score"]
        .agg(["count", "mean"])
        .rename(columns={"count": "场次", "mean": "平均得分"})
        .sort_values(by="平均得分", ascending=False)
    )

    return stats.reset_index()
def show_recommend_page():
    st.title("求生者推荐系统")

    df = load_data()

    if df.empty:
        st.error("数据加载失败或为空。")
        return

    maps = sorted(df["map"].dropna().unique())
    hunters = sorted(df["picks_hunter"].dropna().unique())

    selected_map = st.selectbox("选择地图", maps)
    selected_hunter = st.selectbox("选择假想屠夫", hunters)

    if st.button("生成推荐"):
        stats = recommend_survivors(df, selected_map, selected_hunter)

        if stats.empty:
            st.warning("没有符合条件的数据。")
        else:
            st.success(f"共找到 {len(stats)} 名求生者的记录")
            st.dataframe(stats, use_container_width=True)
            st.bar_chart(data=stats.set_index("survivor")["平均得分"].head(10))
