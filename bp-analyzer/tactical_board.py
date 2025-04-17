import streamlit as st
import streamlit.components.v1 as components

def show_tactical_board(map_url: str):
    st.markdown("### 战术部署区（请拖动求生者到地图上进行布置）")

    components.html(
        f"""
        <style>
            #map {{
                position: relative;
                width: 700px;
                height: 500px;
                background-image: url('{map_url}');
                background-size: cover;
                border: 2px solid #666;
                border-radius: 10px;
            }}
            .survivor {{
                width: 80px;
                height: 80px;
                background-color: rgba(176, 176, 176, 0.7);
                position: absolute;
                cursor: move;
                border-radius: 5px;
                text-align: center;
                line-height: 40px;
                font-weight: bold;
                color: black;
            }}
        </style>
        <div id="map">
            <div class="survivor" style="top: 50px; left: 50px;" draggable="true" id="s1">1</div>
            <div class="survivor" style="top: 100px; left: 50px;" draggable="true" id="s2">2</div>
            <div class="survivor" style="top: 150px; left: 50px;" draggable="true" id="s3">3</div>
            <div class="survivor" style="top: 200px; left: 50px;" draggable="true" id="s4">4</div>
        </div>

        <script>
            const survivors = document.querySelectorAll('.survivor');
            let offsetX = 0, offsetY = 0, draggedEl = null;

            survivors.forEach(el => {{
                el.addEventListener('dragstart', e => {{
                    draggedEl = e.target;
                    offsetX = e.offsetX;
                    offsetY = e.offsetY;
                }});
            }});

            const map = document.getElementById('map');
            map.addEventListener('dragover', e => {{
                e.preventDefault();
            }});
            map.addEventListener('drop', e => {{
                e.preventDefault();
                if (draggedEl) {{
                    draggedEl.style.left = (e.offsetX - offsetX) + 'px';
                    draggedEl.style.top = (e.offsetY - offsetY) + 'px';
                }}
            }});
        </script>
        """,
        height=450
    )
