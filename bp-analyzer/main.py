import streamlit as st
from utils import save_to_excel,is_duplicate_entry
from config import maps_cn_en, survivor_cn_en, hunter_cn_en
from analysis import (
    load_data,
    hunter_winrate_analysis,
    survivor_impact_analysis,
    ban_pick_heatmap_analysis,
    survivor_combo_analysis,
    ban_survivor_effect,
    hunter_winrate_by_map,
    survivor_winrate_by_map
)
import altair as alt
import pandas as pd
from recommend_su import show_recommend_page
from recommend_hu import show_hunter_recommend_page
from tactical_board import show_tactical_board


st.set_page_config(page_title="第五人格 BP 小助手", layout="wide")
st.title("第五人格 BP 小助手")

# 选择功能页面
page = st.sidebar.radio("选择功能", ["首页", "手动录入战报","数据分析","求生者推荐","监管者推荐","战术部署"])

if page == "首页":
    st.header("欢迎来到 BP 数据分析小程序！")
    st.write("你可以在侧边栏选择其他功能，如手动录入战报信息。")
elif page == "手动录入战报":
    st.header("战报信息手动录入")

    # ==== 中文角色 & 地图列表 ====
    MAP_NAMES_CN = ["未选择"] + list(maps_cn_en.keys())
    SURVIVOR_NAMES_CN = ["未选择"] + list(survivor_cn_en.keys())
    HUNTER_NAMES_CN = ["未选择"] + list(hunter_cn_en.keys())

    # ✅ 比赛类型选择（放在表单外部以动态响应）
    bo_type = st.selectbox("比赛类型（决定监管者 Ban 数量）", ["BO1", "BO2", "BO3", "BO5"])
    if bo_type == "BO1":
        hunter_ban_count = 0
    elif bo_type == "BO2":
        hunter_ban_count = 1
    elif bo_type in ["BO3", "BO5"]:
        hunter_ban_count = 2

    st.write(f"当前选择的比赛类型: {bo_type}")
    st.write(f"计算出的监管者Ban数量: {hunter_ban_count}")

    with st.form("manual_form"):
        match_id = st.text_input("比赛 ID(赛事+日期 例如：COA8 418）")
        game_map_cn = st.selectbox("地图（中文）", options=MAP_NAMES_CN)
        team_A = st.text_input("求生者队伍（请使用全大写）")
        team_B = st.text_input("监管者队伍（请使用全大写）")

        st.markdown("### 求生者 Pick（共4人）")
        picks_survivor_cn = []
        for i in range(4):
            name_cn = st.selectbox(f"求生者 Pick {i+1}", options=SURVIVOR_NAMES_CN, key=f"pick_survivor_{i}")
            picks_survivor_cn.append(name_cn.strip())

        st.markdown("### 求生者 Ban（共4人）")
        bans_survivor_cn = []
        for i in range(4):
            name_cn = st.selectbox(f"求生者 Ban {i+1}", options=SURVIVOR_NAMES_CN, key=f"ban_survivor_{i}")
            bans_survivor_cn.append(name_cn.strip())

        st.markdown(f"### 监管者 Pick")
        pick_hunter_cn = st.selectbox("监管者 Pick", options=HUNTER_NAMES_CN, key="pick_hunter")

        st.markdown(f"### 监管者 Ban（共{hunter_ban_count}人）")
        bans_hunter_cn = []
        for i in range(hunter_ban_count):
            name_cn = st.selectbox(f"监管者 Ban {i+1}", options=HUNTER_NAMES_CN, key=f"ban_hunter_{i}")
            bans_hunter_cn.append(name_cn.strip())

        result = st.selectbox("比分结果", options=["未选择", "0:5", "1:3", "2:2", "3:1", "5:0"])
        notes = st.text_area("战局描述")

        submitted = st.form_submit_button("保存数据到 Excel")

    if submitted:
        if not match_id or not game_map_cn or not team_A or not team_B:
            st.warning("请确保填写了比赛 ID、地图和队伍信息。")
        elif is_duplicate_entry(match_id, team_A, team_B, bo_type):
            st.warning(f"⚠️ 这场 BO 记录已存在：{match_id} - {team_A} vs {team_B} - {bo_type}")
        else:
            try:
                map_code = maps_cn_en.get(game_map_cn, f"[未知地图: {game_map_cn}]")

                picks_survivor = [
                    survivor_cn_en.get(name, f"[未知求生者: {name}]")
                    for name in picks_survivor_cn
                ]

                bans_survivor = [
                    survivor_cn_en.get(name, f"[未知求生者: {name}]")
                    for name in bans_survivor_cn
                ]

                pick_hunter = hunter_cn_en.get(pick_hunter_cn, f"[未知监管者: {pick_hunter_cn}]")

                bans_hunter = [
                    hunter_cn_en.get(name, f"[未知监管者: {name}]")
                    for name in bans_hunter_cn
                ]

                final_data = {
                    "match_id": match_id,
                    "map": map_code,
                    "team_survivor": team_A,
                    "team_hunter": team_B,
                    "bo_type": bo_type,
                    "picks_survivor": picks_survivor,
                    "picks_hunter": pick_hunter,
                    "bans_hunter": bans_hunter,
                    "bans_survivor": bans_survivor,
                    "result": result,
                    "notes": notes,
                    "raw_cn": {
                        "map": game_map_cn,
                        "picks_survivor": picks_survivor_cn,
                        "pick_hunter": pick_hunter_cn,
                        "bans_survivor": bans_survivor_cn,
                        "bans_hunter": bans_hunter_cn,
                    }
                }

                save_to_excel(final_data)
                st.success("✅ 数据已成功保存到 `bp_data.xlsx`！")
            except Exception as e:
                st.error(f"❌ 保存失败，错误信息：{e}")

elif page == "数据分析":
    st.header("📊 BP 数据分析")

    try:
        df = load_data()
        st.success("数据加载成功！")

        analysis_option = st.selectbox("选择分析内容", [
            "猎人胜率",
            "求生者角色影响",
            "Ban/Pick 热度",
            "求生者组合效果",
            "Ban求生者影响",
            "求生者在不同地图上的胜率",
            "地图对屠夫胜率的影响"

        ])

        # Analysis options
        if analysis_option == "猎人胜率":
            result_df = hunter_winrate_analysis(df)
            st.subheader("猎人胜率分析")
            st.dataframe(result_df)

            st.markdown("#### 胜/平/负 对比图")
            st.bar_chart(result_df[["win", "draw", "lose"]])

            st.markdown("#### 胜率图（按 winrate 排序）")
            sorted_winrate = result_df.sort_values(by="winrate", ascending=True)
            st.bar_chart(sorted_winrate["winrate"])

        elif analysis_option == "求生者角色影响":
            result_df = survivor_impact_analysis(df)
            st.subheader("求生者角色胜负影响分析")
            st.dataframe(result_df)

            st.markdown("#### 胜/平/负 堆叠图")
            melted = result_df.reset_index().melt(
                id_vars="index", value_vars=["win", "draw", "lose"]
            )
            melted.columns = ["survivor", "result", "count"]

            chart = alt.Chart(melted).mark_bar().encode(
                x=alt.X("survivor:N", title="求生者角色", sort='-x'),
                y=alt.Y("count:Q", title="场次"),
                color="result:N",
                facet=alt.Facet("result:N", columns=3),  # 按结果类型分面，展示多个小图
                tooltip=["survivor:N", "result:N", "count:Q"]
            ).properties(width=200, height=300)

            st.altair_chart(chart)

        elif analysis_option == "Ban/Pick 热度":
            st.subheader("BP 热度统计")
            stats = ban_pick_heatmap_analysis(df)

            st.markdown("#### 求生者 Pick 热度图")
            survivor_pick_series = pd.Series(stats["pick_counts_survivor"]).sort_values(ascending=False)
            st.bar_chart(survivor_pick_series)

            st.markdown("#### 监管者 Pick 热度图")
            hunter_pick_series = pd.Series(stats["pick_counts_hunter"]).sort_values(ascending=False)
            st.bar_chart(hunter_pick_series)

            st.markdown("#### 求生者 Ban 热度图")
            survivor_ban_series = pd.Series(stats["ban_counts_survivor"]).sort_values(ascending=False)
            st.bar_chart(survivor_ban_series)

            st.markdown("#### 监管者 Ban 热度图")
            hunter_ban_series = pd.Series(stats["ban_counts_hunter"]).sort_values(ascending=False)
            st.bar_chart(hunter_ban_series)

        elif analysis_option == "求生者组合效果":
            result_df = survivor_combo_analysis(df)
            st.subheader("求生者组合效果分析")
            st.dataframe(result_df)

        elif analysis_option == "Ban求生者影响":
            result_df = ban_survivor_effect(df)
            st.subheader("被 Ban 求生者对胜率的影响")
            st.dataframe(result_df)
        elif analysis_option == "求生者在不同地图上的胜率":
            # 计算求生者在每个地图上的胜率
            result_df = survivor_winrate_by_map(df)

            # 按地图进行分组
            maps = result_df["map"].unique()

            # 显示每个地图的求生者胜率
            for map_name in maps:
                st.subheader(f"{map_name} 地图胜率分析")

                # 获取当前地图的求生者数据
                map_df = result_df[result_df["map"] == map_name]

                # 按胜率排序
                map_df_sorted = map_df.sort_values(by="winrate", ascending=False)

                # 显示该地图下的求生者胜率列表
                st.dataframe(map_df_sorted)

                # 显示该地图的求生者胜率条形图
                st.markdown(f"#### {map_name} 地图求生者胜率条形图")
                st.bar_chart(map_df_sorted.set_index('survivor')['winrate'])

        elif analysis_option == "地图对屠夫胜率的影响":
            result_df = hunter_winrate_by_map(df)
            st.subheader("地图胜率分析")
            st.dataframe(result_df)

            st.markdown("#### 各地图胜率条形图")
            st.bar_chart(result_df["winrate"])

    except Exception as e:
        st.error(f"❌ 数据加载失败：{e}")
if page == "求生者推荐":
    show_recommend_page()
if page == "监管者推荐":
    show_hunter_recommend_page()
if page == "战术部署":
    st.header("战术部署模拟器")
    MAP_NAMES_CN = ["未选择"] + list(maps_cn_en.keys())
    SURVIVOR_NAMES_CN = ["未选择"] + list(survivor_cn_en.keys())
    HUNTER_NAMES_CN = ["未选择"] + list(hunter_cn_en.keys())

    # 地图和监管者选择
    map_choice = st.sidebar.selectbox("选择地图",MAP_NAMES_CN)
    hunter_choice = st.sidebar.selectbox("假想监管者", HUNTER_NAMES_CN)

    # 地图链接字典
    map_dict = {
        "军工厂": "https://i.imgur.com/Nx2DPwC.jpeg",
        "里奥的回忆": "https://i.imgur.com/Nx2DPwC.jpeg",
        "圣心医院": "https://i.imgur.com/Nx2DPwC.jpeg"
    }
    map_url = map_dict.get(map_choice, map_dict["军工厂"])

    # 显示战术部署图
    show_tactical_board(map_url)