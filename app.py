import html

import folium
import streamlit as st
from folium import plugins
from streamlit_folium import st_folium


st.set_page_config(
    page_title="남산 PGIS — 주민참여형 공간정보시스템",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSET_TYPES = [
    {"id": "history", "label": "역사 자산", "icon": "史", "color": "#fb923c", "bg": "rgba(251,146,60,0.15)"},
    {"id": "life", "label": "생활 자산", "icon": "生", "color": "#4ecdc4", "bg": "rgba(78,205,196,0.15)"},
    {"id": "culture", "label": "문화 자산", "icon": "文", "color": "#a78bfa", "bg": "rgba(167,139,250,0.15)"},
    {"id": "ecology", "label": "생태 자산", "icon": "森", "color": "#34d399", "bg": "rgba(52,211,153,0.15)"},
    {"id": "landscape", "label": "경관 자산", "icon": "景", "color": "#4a9eff", "bg": "rgba(74,158,255,0.15)"},
    {"id": "community", "label": "공동체 자산", "icon": "共", "color": "#f472b6", "bg": "rgba(244,114,182,0.15)"},
]

ASSETS = [
    {"id": 1, "name": "한양도성 남산구간", "type": "history", "lat": 37.5512, "lng": 126.9882, "zone": "예장동", "desc": "서울 한양도성의 남산 구간으로, 조선시대부터 이어진 성곽길입니다. 약 1.3km에 걸쳐 성벽이 보존되어 있으며, 도성 안팎의 경관을 조망할 수 있습니다.", "tags": ["조선시대", "성곽", "순성길"]},
    {"id": 2, "name": "108계단", "type": "life", "lat": 37.5445, "lng": 126.9785, "zone": "후암동", "desc": "후암동에서 해방촌으로 오르는 108개의 계단으로, 주민들의 일상적 이동 경로이자 남산 경사지 마을의 상징적 장소입니다.", "tags": ["계단길", "생활동선", "해방촌"]},
    {"id": 3, "name": "남산골한옥마을", "type": "culture", "lat": 37.5590, "lng": 126.9942, "zone": "예장동", "desc": "전통 한옥 5동과 전통정원, 타임캡슐광장 등으로 구성된 전통문화 체험 공간입니다.", "tags": ["한옥", "전통문화", "체험"]},
    {"id": 4, "name": "남산 소나무 숲길", "type": "ecology", "lat": 37.5505, "lng": 126.9880, "zone": "남산 정상부", "desc": "남산 북측 사면의 소나무 군락지로, 도심 속 귀중한 도시생태 자원입니다. 다양한 조류와 곤충이 관찰됩니다.", "tags": ["소나무", "도시생태", "숲길"]},
    {"id": 5, "name": "N서울타워 전망대", "type": "landscape", "lat": 37.5512, "lng": 126.9882, "zone": "남산 정상부", "desc": "해발 480m 높이에서 서울 전역을 360도 조망할 수 있는 대표적 조망점입니다.", "tags": ["전망", "야경", "랜드마크"]},
    {"id": 6, "name": "해방촌 골목길", "type": "life", "lat": 37.5432, "lng": 126.9810, "zone": "후암동", "desc": "해방 이후 형성된 마을의 좁은 골목길로, 다양한 문화와 세대가 공존하는 생활 공간입니다.", "tags": ["골목", "다문화", "생활문화"]},
    {"id": 7, "name": "남대문시장", "type": "life", "lat": 37.5592, "lng": 126.9773, "zone": "회현동", "desc": "600년 전통의 대한민국 대표 재래시장으로, 다양한 상품과 먹거리가 있는 생활·관광 자원입니다.", "tags": ["전통시장", "상권", "먹거리"]},
    {"id": 8, "name": "장충단공원", "type": "history", "lat": 37.5575, "lng": 127.0015, "zone": "장충동", "desc": "대한제국기 장충단이 있던 곳으로, 순국선열의 넋을 기리기 위해 조성된 역사공원입니다.", "tags": ["대한제국", "순국선열", "역사공원"]},
    {"id": 9, "name": "국립극장", "type": "culture", "lat": 37.5530, "lng": 127.0045, "zone": "장충동", "desc": "1950년 개관한 대한민국 최초의 국립극장으로, 남산 자락에 위치한 대표적 공연예술 시설입니다.", "tags": ["공연", "예술", "문화시설"]},
    {"id": 10, "name": "봉수대", "type": "history", "lat": 37.5505, "lng": 126.9870, "zone": "남산 정상부", "desc": "조선시대 전국의 봉수 신호를 최종 수신하던 곳으로, 남산 정상에 위치한 역사유적입니다.", "tags": ["조선시대", "통신", "정상"]},
    {"id": 11, "name": "백범광장", "type": "community", "lat": 37.5555, "lng": 126.9755, "zone": "회현동", "desc": "김구 선생의 동상이 있는 시민 광장으로, 주민과 시민의 모임·행사 공간으로 활용됩니다.", "tags": ["광장", "시민공간", "김구"]},
    {"id": 12, "name": "예장자락길", "type": "ecology", "lat": 37.5565, "lng": 126.9905, "zone": "예장동", "desc": "남산 북측 자락을 따라 조성된 산책로로, 도심 속 녹지축을 연결하는 생태 보행로입니다.", "tags": ["산책로", "녹지축", "자락길"]},
    {"id": 13, "name": "이태원 남산 조망점", "type": "landscape", "lat": 37.5405, "lng": 126.9920, "zone": "이태원동", "desc": "이태원 고지대에서 남산과 N서울타워를 조망할 수 있는 숨은 전망 포인트입니다.", "tags": ["조망", "야경", "숨은명소"]},
    {"id": 14, "name": "용산신학교 터", "type": "history", "lat": 37.5430, "lng": 126.9795, "zone": "후암동", "desc": "근대 선교 역사의 흔적이 남아있는 장소로, 개화기 서양 문화 유입의 통로였던 역사자원입니다.", "tags": ["근대사", "선교", "개화기"]},
    {"id": 15, "name": "옛 중앙정보부 터", "type": "history", "lat": 37.5580, "lng": 126.9920, "zone": "예장동", "desc": "현대사의 굴곡을 상징하는 장소로, 현재는 시민에게 개방된 공원으로 변모하고 있습니다.", "tags": ["현대사", "정치", "도시재생"]},
    {"id": 16, "name": "남산순환도로 야경 포인트", "type": "landscape", "lat": 37.5490, "lng": 126.9930, "zone": "남산 정상부", "desc": "남산 순환도로에서 서울 도심의 야경을 감상할 수 있는 대표적 야간 조망 포인트입니다.", "tags": ["야경", "도심조망", "드라이브"]},
    {"id": 17, "name": "동국대 일대 숲길", "type": "ecology", "lat": 37.5580, "lng": 127.0000, "zone": "장충동", "desc": "동국대학교 캠퍼스와 연결된 남산 동측 숲길로, 참나무류와 단풍나무가 어우러진 산책 코스입니다.", "tags": ["숲길", "캠퍼스", "단풍"]},
    {"id": 18, "name": "회현지하상가", "type": "life", "lat": 37.5585, "lng": 126.9790, "zone": "회현동", "desc": "1970년대 조성된 지하상가로, 수선·맞춤 등 전통 기술이 남아있는 독특한 상업 공간입니다.", "tags": ["지하상가", "수선", "근대상업"]},
]

ROUTES = [
    {"id": "r1", "name": "남산 생활기억길", "color": "#4ecdc4", "icon": "生", "distance": "3.2km", "duration": "1.5시간", "difficulty": "보통", "desc": "후암동·회현동 일대 주민 생활골목과 계단길을 잇는 루트. 오래된 가게, 골목 풍경, 주민의 장소 기억을 따라 걷습니다.", "points": [2, 6, 18, 7], "zones": ["후암동", "회현동"]},
    {"id": "r2", "name": "남산 역사문화길", "color": "#fb923c", "icon": "史", "distance": "4.1km", "duration": "2시간", "difficulty": "보통", "desc": "한양도성부터 근현대 역사 자원까지, 남산의 시간 층위를 체험하는 역사 탐방 루트입니다.", "points": [1, 10, 15, 8, 3], "zones": ["예장동", "장충동"]},
    {"id": "r3", "name": "남산 조망길", "color": "#4a9eff", "icon": "景", "distance": "3.8km", "duration": "2시간", "difficulty": "어려움", "desc": "서울의 스카이라인과 야경을 감상할 수 있는 조망 포인트를 연결하는 전망 루트입니다.", "points": [5, 16, 13], "zones": ["남산 정상부", "이태원동"]},
    {"id": "r4", "name": "남산 생태길", "color": "#34d399", "icon": "森", "distance": "2.8km", "duration": "1.5시간", "difficulty": "쉬움", "desc": "남산의 숲길과 녹지축을 따라 도시생태를 관찰하고 체험하는 자연 탐방 루트입니다.", "points": [4, 12, 17], "zones": ["남산 정상부", "예장동", "장충동"]},
    {"id": "r5", "name": "남산 공동체길", "color": "#f472b6", "icon": "共", "distance": "2.5km", "duration": "1시간", "difficulty": "쉬움", "desc": "주민 커뮤니티 공간과 마을 활동 거점을 연결하여 세대·문화 간 교류를 촉진하는 루트입니다.", "points": [11, 7, 6], "zones": ["회현동", "후암동"]},
]

ROUTE_PATHS = {
    "r1": [
        [37.5445, 126.9785], [37.5438, 126.9792], [37.5432, 126.9810],
        [37.5450, 126.9820], [37.5480, 126.9815], [37.5520, 126.9804],
        [37.5560, 126.9794], [37.5585, 126.9790], [37.5592, 126.9773],
    ],
    "r2": [
        [37.5512, 126.9882], [37.5505, 126.9870], [37.5514, 126.9888],
        [37.5535, 126.9903], [37.5560, 126.9913], [37.5580, 126.9920],
        [37.5588, 126.9935], [37.5590, 126.9942], [37.5586, 126.9965],
        [37.5580, 126.9992], [37.5575, 127.0015],
    ],
    "r3": [
        [37.5512, 126.9882], [37.5506, 126.9905], [37.5490, 126.9930],
        [37.5473, 126.9938], [37.5454, 126.9940], [37.5432, 126.9932],
        [37.5405, 126.9920],
    ],
    "r4": [
        [37.5505, 126.9880], [37.5520, 126.9885], [37.5542, 126.9890],
        [37.5565, 126.9905], [37.5571, 126.9930], [37.5574, 126.9960],
        [37.5580, 127.0000],
    ],
    "r5": [
        [37.5555, 126.9755], [37.5570, 126.9761], [37.5592, 126.9773],
        [37.5585, 126.9790], [37.5558, 126.9796], [37.5515, 126.9802],
        [37.5470, 126.9808], [37.5432, 126.9810],
    ],
}

ZONES = [
    {"id": "huam", "name": "후암동", "desc": "생활골목, 계단길, 주거지 풍경", "color": "#4ecdc4"},
    {"id": "hoehyeon", "name": "회현동", "desc": "시장·관광 연결축", "color": "#fb923c"},
    {"id": "yejang", "name": "예장동", "desc": "역사문화·남산 접근축", "color": "#a78bfa"},
    {"id": "jangchung", "name": "장충동", "desc": "문화시설·숲길", "color": "#34d399"},
    {"id": "itaewon", "name": "이태원동", "desc": "다문화·경관·조망 자산", "color": "#4a9eff"},
    {"id": "summit", "name": "남산 정상부", "desc": "순환형 탐방·조망 공간", "color": "#f7c948"},
]

TYPE_BY_ID = {item["id"]: item for item in ASSET_TYPES}
ASSET_BY_ID = {item["id"]: item for item in ASSETS}


def inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700;900&display=swap');
        :root {
          --bg:#f8fafc; --bg2:#ffffff; --bg3:#f1f5f9;
          --accent:#0f766e; --gold:#ca8a04; --text:#0f172a; --text2:#64748b;
          --border:#dbe3ee; --radius:12px;
        }
        html, body, [class*="css"], .stApp {
          font-family:'Noto Sans KR',sans-serif;
          background:var(--bg);
          color:var(--text);
        }
        .main .block-container {padding:1rem 1.25rem 1.5rem; max-width:100%;}
        [data-testid="stSidebar"] {background:var(--bg2); border-right:1px solid var(--border);}
        [data-testid="stSidebar"] > div {padding-top:1.1rem;}
        h1, h2, h3, h4, p, label, span, div {letter-spacing:0;}
        .brand-title {font-size:18px;font-weight:700;margin:0 0 2px;}
        .brand-title span {color:var(--accent);}
        .subtitle {font-size:11px;color:var(--text2);margin-bottom:18px;}
        div[data-testid="stRadio"] label {font-size:12px;color:var(--text2);}
        div[data-testid="stRadio"] > div {gap:4px;}
        div[data-testid="stRadio"] [role="radiogroup"] label {
          background:var(--bg3); border:1px solid var(--border); border-radius:8px;
          padding:8px 10px; margin-bottom:2px;
        }
        .card {
          background:var(--bg3);border:1px solid var(--border);border-radius:var(--radius);
          padding:16px;margin-bottom:12px;transition:all .2s;
        }
        .card:hover {border-color:var(--accent);transform:translateY(-1px);}
        .card-header {display:flex;align-items:center;gap:10px;margin-bottom:8px;}
        .card-icon {width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;line-height:1;flex-shrink:0;}
        .card-title {font-size:14px;font-weight:600;color:var(--text);}
        .card-sub {font-size:11px;color:var(--text2);}
        .card-desc {font-size:12px;color:var(--text2);line-height:1.6;}
        .card-tags {display:flex;gap:6px;margin-top:10px;flex-wrap:wrap;}
        .card-tag {font-size:10px;padding:3px 8px;border-radius:20px;background:rgba(78,205,196,.1);color:var(--accent);border:1px solid rgba(78,205,196,.2);}
        .route-card {position:relative;overflow:hidden;padding-left:20px;}
        .route-line {position:absolute;left:0;top:0;bottom:0;width:4px;}
        .route-meta {display:flex;gap:12px;margin-top:10px;font-size:11px;color:var(--text2);flex-wrap:wrap;}
        .chip-row {display:flex;gap:6px;flex-wrap:wrap;margin:2px 0 12px;}
        .chip {padding:5px 12px;border-radius:20px;font-size:11px;border:1px solid var(--border);color:var(--text2);}
        .chip.active {border-color:var(--accent);color:var(--accent);background:rgba(78,205,196,.1);}
        .asset-history{background:rgba(251,146,60,.15);color:#fb923c}
        .asset-life{background:rgba(78,205,196,.15);color:#4ecdc4}
        .asset-culture{background:rgba(167,139,250,.15);color:#a78bfa}
        .asset-ecology{background:rgba(52,211,153,.15);color:#34d399}
        .asset-landscape{background:rgba(74,158,255,.15);color:#4a9eff}
        .asset-community{background:rgba(244,114,182,.15);color:#f472b6}
        .map-shell {position:relative;border:1px solid var(--border);border-radius:12px;overflow:hidden;background:var(--bg2);}
        .legend, .pgis-panel, .stats-bar {
          background:rgba(255,255,255,.96);border:1px solid var(--border);border-radius:var(--radius);
          box-shadow:0 8px 28px rgba(15,23,42,.10);
          height:180px;box-sizing:border-box;
        }
        .legend {padding:18px 16px 14px;}
        .legend h4 {font-size:13px;font-weight:700;margin:0 0 12px;color:var(--accent);}
        .legend-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;}
        .legend-item {
          display:flex;align-items:center;gap:7px;min-width:0;padding:6px 7px;border:1px solid rgba(15,23,42,.06);
          border-radius:10px;background:rgba(248,250,252,.78);font-size:10px;font-weight:600;color:var(--text);
        }
        .legend-picture {flex:0 0 28px;width:28px;height:28px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:800;line-height:1;border:1px solid rgba(15,23,42,.08);}
        .legend-label {min-width:0;white-space:nowrap;}
        .stats-bar {display:flex;align-items:center;gap:2px;overflow:hidden;}
        .stat-item {padding:12px 18px;text-align:center;flex:1;}
        .stat-value {font-size:18px;font-weight:700;color:var(--accent);}
        .stat-label {font-size:10px;color:var(--text2);margin-top:2px;}
        .pgis-panel {padding:16px;}
        .pgis-panel h4 {font-size:13px;font-weight:600;margin-bottom:12px;display:flex;align-items:center;gap:6px;}
        .dot {width:8px;height:8px;background:#34d399;border-radius:50%;display:inline-block;animation:pulse 2s infinite;}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
        .type-badge {display:inline-block;padding:4px 12px;border-radius:20px;font-size:11px;margin-bottom:10px;}
        .detail-symbol {width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;line-height:1;margin-bottom:12px;}
        .detail-box {background:var(--bg2);border:1px solid var(--border);border-radius:12px;padding:20px;height:100%;}
        .detail-box h2 {font-size:20px;font-weight:700;margin:0 0 8px;}
        .detail-box p {font-size:13px;color:var(--text2);line-height:1.8;}
        .about-text {font-size:12px;color:var(--text2);line-height:1.8;margin-bottom:16px;}
        .info-grid {display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px;}
        .info-box {background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center;}
        .info-box .val {font-size:18px;font-weight:700;color:var(--accent);}
        .info-box .lbl {font-size:10px;color:var(--text2);margin-top:4px;}
        .leaflet-container {background:#f4f4f0 !important;}
        .leaflet-popup-content-wrapper {background:#ffffff !important;color:#0f172a !important;border:1px solid #dbe3ee !important;border-radius:12px !important;}
        .leaflet-popup-tip {background:#ffffff !important;}
        .stButton > button, .stDownloadButton > button {
          border-radius:8px;border:1px solid var(--border);background:var(--bg3);color:var(--text);
          font-family:'Noto Sans KR',sans-serif;
        }
        .stButton > button:hover {border-color:var(--accent);color:var(--accent);}
        .primary-action > button, button[kind="primary"] {background:var(--accent)!important;color:#ffffff!important;border-color:var(--accent)!important;}
        input, textarea, select {background:var(--bg3)!important;color:var(--text)!important;border-color:var(--border)!important;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def esc(value):
    return html.escape(str(value), quote=True)


def render_asset_card(asset):
    asset_type = TYPE_BY_ID[asset["type"]]
    tags = "".join(f'<span class="card-tag">{esc(tag)}</span>' for tag in asset["tags"])
    return f"""
    <div class="card">
      <div class="card-header">
        <div class="card-icon asset-{asset['type']}">{asset_type['icon']}</div>
        <div><div class="card-title">{esc(asset['name'])}</div><div class="card-sub">{esc(asset['zone'])}</div></div>
      </div>
      <div class="card-desc">{esc(asset['desc'][:80])}...</div>
      <div class="card-tags">{tags}</div>
    </div>
    """


def render_route_card(route, active):
    border = f"border-color:{route['color']};" if active else ""
    return f"""
    <div class="card route-card" style="{border}">
      <div class="route-line" style="background:{route['color']}"></div>
      <div class="card-header">
        <div class="card-icon" style="background:{route['color']}22;color:{route['color']}">{route['icon']}</div>
        <div><div class="card-title">{esc(route['name'])}</div><div class="card-sub" style="color:{route['color']}">{esc(' → '.join(route['zones']))}</div></div>
      </div>
      <div class="card-desc">{esc(route['desc'])}</div>
      <div class="route-meta">
        <span>거리 {esc(route['distance'])}</span><span>시간 {esc(route['duration'])}</span>
        <span>난이도 {esc(route['difficulty'])}</span><span>거점 {len(route['points'])}개</span>
      </div>
    </div>
    """


def marker_html(asset):
    asset_type = TYPE_BY_ID[asset["type"]]
    return f"""
    <div style="width:32px;height:32px;border-radius:50%;background:{asset_type['bg']};
    border:2px solid {asset_type['color']};display:flex;align-items:center;justify-content:center;
    font-size:13px;font-weight:800;line-height:1;cursor:pointer;box-shadow:0 2px 8px rgba(15,23,42,.18)">{asset_type['icon']}</div>
    """


def popup_html(asset):
    asset_type = TYPE_BY_ID[asset["type"]]
    tags = "".join(
        f"<span style='font-size:10px;padding:2px 8px;border-radius:12px;background:{asset_type['bg']};color:{asset_type['color']}'>{esc(tag)}</span>"
        for tag in asset["tags"]
    )
    return f"""
    <div style="min-width:180px">
      <div style="font-size:14px;font-weight:600;margin-bottom:4px">{asset_type['icon']} {esc(asset['name'])}</div>
      <div style="font-size:11px;color:#64748b;margin-bottom:8px">{esc(asset['zone'])}</div>
      <div style="font-size:12px;line-height:1.6;color:#0f172a">{esc(asset['desc'][:80])}...</div>
      <div style="margin-top:8px;display:flex;gap:4px;flex-wrap:wrap">{tags}</div>
    </div>
    """


def route_path(route):
    path = ROUTE_PATHS.get(route["id"])
    if path:
        return path
    return [[ASSET_BY_ID[pid]["lat"], ASSET_BY_ID[pid]["lng"]] for pid in route["points"] if pid in ASSET_BY_ID]


def make_map(filtered_assets, active_route):
    route = next((item for item in ROUTES if item["id"] == active_route), None)
    center = [37.5505, 126.988]
    zoom = 15
    if route:
        path = route_path(route)
        if path:
            center = [sum(p[0] for p in path) / len(path), sum(p[1] for p in path) / len(path)]
            zoom = 14

    fmap = folium.Map(
        location=center,
        zoom_start=zoom,
        zoom_control=False,
        tiles=None,
        control_scale=True,
    )
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="&copy; CARTO",
        max_zoom=19,
        name="CartoDB Positron",
    ).add_to(fmap)
    plugins.Fullscreen(position="topright").add_to(fmap)
    plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(fmap)

    for asset in filtered_assets:
        folium.Marker(
            location=[asset["lat"], asset["lng"]],
            popup=folium.Popup(popup_html(asset), max_width=260),
            tooltip=asset["name"],
            icon=folium.DivIcon(html=marker_html(asset), icon_size=(32, 32), icon_anchor=(16, 16)),
        ).add_to(fmap)

    if route:
        path = route_path(route)
        if len(path) > 1:
            folium.PolyLine(path, color=route["color"], weight=4, opacity=0.85, dash_array="10,6").add_to(fmap)
            fmap.fit_bounds(path, padding=(60, 60))
    return fmap


def sync_clicked_asset(map_state):
    clicked = map_state.get("last_object_clicked") if map_state else None
    if not clicked:
        return
    lat = round(clicked.get("lat", 0), 4)
    lng = round(clicked.get("lng", 0), 4)
    for asset in ASSETS:
        if round(asset["lat"], 4) == lat and round(asset["lng"], 4) == lng:
            st.session_state.selected_asset_id = asset["id"]
            break


def render_detail(asset):
    asset_type = TYPE_BY_ID[asset["type"]]
    route_matches = [route for route in ROUTES if asset["id"] in route["points"]]
    tags = "".join(f'<span class="card-tag">{esc(tag)}</span>' for tag in asset["tags"])
    routes = "".join(
        f"""<div style="display:flex;align-items:center;gap:8px;padding:8px 0;font-size:12px">
        <div style="width:8px;height:8px;border-radius:50%;background:{route['color']}"></div>{esc(route['name'])} ({esc(route['distance'])})
        </div>"""
        for route in route_matches
    ) or '<div style="font-size:12px;color:var(--text2)">연결된 루트 없음</div>'
    st.markdown(
        f"""
        <div class="detail-box">
          <div class="detail-symbol asset-{asset['type']}">{asset_type['icon']}</div>
          <h2>{esc(asset['name'])}</h2>
          <div class="type-badge" style="background:{asset_type['bg']};color:{asset_type['color']}">{esc(asset_type['label'])}</div>
          <div style="font-size:12px;color:var(--text2);margin-bottom:16px">위치 {esc(asset['zone'])} · {asset['lat']:.4f}, {asset['lng']:.4f}</div>
          <p>{esc(asset['desc'])}</p>
          <div style="margin:18px 0 8px;color:var(--accent);font-size:14px;font-weight:600">태그</div>
          <div class="card-tags">{tags}</div>
          <div style="margin:18px 0 8px;color:var(--accent);font-size:14px;font-weight:600">연결 루트</div>
          {routes}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_assets_tab(filtered_assets):
    st.markdown(
        '<div class="chip-row">'
        + "".join(
            f'<span class="chip active" style="border-color:{TYPE_BY_ID[t]["color"]};color:{TYPE_BY_ID[t]["color"]};background:{TYPE_BY_ID[t]["bg"]}">{TYPE_BY_ID[t]["icon"]} {TYPE_BY_ID[t]["label"]}</span>'
            for t in st.session_state.active_filters
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"{len(filtered_assets)}개 자산 표시 중")
    for asset in filtered_assets:
        st.markdown(render_asset_card(asset), unsafe_allow_html=True)
        if st.button("상세 보기", key=f"asset_{asset['id']}", use_container_width=True):
            st.session_state.selected_asset_id = asset["id"]


def render_routes_tab():
    st.markdown(
        '<div class="about-text">남산 일대의 지역자산을 연계한 5개 주제별 보행 네트워크입니다.</div>',
        unsafe_allow_html=True,
    )
    route_options = ["선택 안 함"] + [route["name"] for route in ROUTES]
    current = next((route["name"] for route in ROUTES if route["id"] == st.session_state.active_route), "선택 안 함")
    selected = st.selectbox("지도에 표시할 루트", route_options, index=route_options.index(current))
    st.session_state.active_route = None if selected == "선택 안 함" else next(route["id"] for route in ROUTES if route["name"] == selected)
    for route in ROUTES:
        st.markdown(render_route_card(route, route["id"] == st.session_state.active_route), unsafe_allow_html=True)
        if st.button("루트 표시" if route["id"] != st.session_state.active_route else "루트 해제", key=f"route_{route['id']}", use_container_width=True):
            st.session_state.active_route = None if route["id"] == st.session_state.active_route else route["id"]
            st.rerun()


def render_pgis_tab():
    st.markdown(
        '<div class="about-text">PGIS(주민참여형 GIS)를 통해 남산의 숨겨진 장소를 직접 등록하고, 지역 자산 지도를 함께 만들어갑니다.</div>',
        unsafe_allow_html=True,
    )
    with st.form("pgis_form", clear_on_submit=True):
        st.subheader("새 장소 등록")
        name = st.text_input("장소 이름 *", placeholder="예: 후암동 옛 우물터")
        asset_type = st.selectbox("자산 유형 *", ASSET_TYPES, format_func=lambda item: f"{item['icon']} {item['label']}")
        zone = st.selectbox("권역 *", ZONES, format_func=lambda item: item["name"])
        desc = st.text_area("장소 설명", placeholder="이 장소에 대한 이야기, 기억, 특징을 적어주세요...")
        tags = st.text_input("태그 (쉼표로 구분)", placeholder="예: 골목길, 추억, 숨은명소")
        submitted = st.form_submit_button("등록하기", type="primary", use_container_width=True)
        if submitted:
            if name.strip():
                st.success("장소가 등록되었습니다! (데모)")
                st.session_state.demo_submissions.append(
                    {
                        "name": name.strip(),
                        "type": asset_type["id"],
                        "zone": zone["name"],
                        "desc": desc.strip(),
                        "tags": [tag.strip() for tag in tags.split(",") if tag.strip()],
                    }
                )
            else:
                st.warning("장소 이름을 입력해주세요.")

    st.markdown("#### 참여 방법 안내")
    for item in [
        ("01", "모바일 장소 등록", "스마트폰으로 위치를 태깅하고 사진·설명을 기록합니다"),
        ("02", "참여형 워크숍", "대형 지도 위에 포스트잇·스티커로 장소를 표시합니다"),
        ("03", "보행 조사", "주민과 함께 걸으며 현장에서 직접 장소를 기록합니다"),
        ("04", "구술 기록", "고령 주민의 장소 기억과 이야기를 녹음·정리합니다"),
        ("05", "사진 조사 (Photovoice)", "주민이 촬영한 사진에 위치·의미를 부여합니다"),
    ]:
        st.markdown(
            f"""<div class="card"><div class="card-header"><div class="card-icon" style="background:rgba(15,118,110,.10);color:var(--accent);font-size:11px">{item[0]}</div>
            <div><div class="card-title">{esc(item[1])}</div></div></div><div class="card-desc">{esc(item[2])}</div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown("#### 수집 데이터 유형")
    for value in ["기억하고 싶은 장소", "걷기 좋은 길", "위험한 길", "숨은 명소", "문화 이야기", "생태 장소", "연결 필요 구간"]:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--border);font-size:12px"><span style="color:var(--accent)">●</span> {esc(value)}</div>',
            unsafe_allow_html=True,
        )


def render_about_tab():
    st.markdown("### 사업 개요")
    st.markdown(
        '<div class="about-text">남산 일대의 역사·문화·생활·생태·경관 자산을 주민과 이용자가 직접 발굴·지도화하여, 지역 고유성을 반영한 지속가능한 보행·문화 네트워크를 구축하는 프로젝트입니다.</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="info-grid">
          <div class="info-box"><div class="val">500+</div><div class="lbl">목표 자산 등록</div></div>
          <div class="info-box"><div class="val">5종</div><div class="lbl">주제별 지도</div></div>
          <div class="info-box"><div class="val">5개</div><div class="lbl">보행 루트</div></div>
          <div class="info-box"><div class="val">5.2km²</div><div class="lbl">대상 면적</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### 대상 권역")
    for zone in ZONES:
        st.markdown(
            f"""<div class="card"><div class="card-header">
            <div style="width:12px;height:12px;border-radius:50%;background:{zone['color']};flex-shrink:0"></div>
            <div><div class="card-title">{esc(zone['name'])}</div><div class="card-sub">{esc(zone['desc'])}</div></div>
            </div></div>""",
            unsafe_allow_html=True,
        )
    st.markdown("### GIS 분석 체계")
    for value in ["경사도 분석 — 보행 편의성 평가", "네트워크 분석 — 연결성 평가", "가시권 분석 — 조망자원 평가", "접근성 분석 — 보행 접근성 평가", "밀도 분석 — 자산 집중지역 도출", "위험도 분석 — 안전성 평가"]:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;padding:8px 0;border-bottom:1px solid var(--border);font-size:12px"><span style="color:var(--accent)">◆</span> {esc(value)}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("### 추진 로드맵 (12개월)")
    for idx, value in enumerate(["1~2개월: 기초 GIS 구축", "2~3개월: 주민 워크숍", "3~5개월: PGIS 장소 수집", "4~6개월: 현장조사", "5~7개월: 공간분석", "7~9개월: 길 네트워크 설계", "9~11개월: 시범구간 운영", "11~12개월: 통합 플랫폼 구축"], start=1):
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:8px;padding:6px 0;font-size:12px;color:var(--text2)"><span style="color:var(--accent);font-weight:700;font-size:11px;min-width:20px">{idx}</span> {esc(value)}</div>',
            unsafe_allow_html=True,
        )


def render_sidebar(filtered_assets):
    with st.sidebar:
        st.markdown('<div class="brand-title">남산 <span>PGIS</span></div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">주민참여형 공간정보시스템 · 남산 길만들기</div>', unsafe_allow_html=True)

        tabs = {
            "자산지도": "assets",
            "길 네트워크": "routes",
            "PGIS 참여": "pgis",
            "사업소개": "about",
        }
        label = st.radio("메뉴", list(tabs.keys()), label_visibility="collapsed")
        st.session_state.active_tab = tabs[label]

        selected_labels = st.multiselect(
            "자산 유형 필터",
            ASSET_TYPES,
            default=[TYPE_BY_ID[item] for item in st.session_state.active_filters],
            format_func=lambda item: f"{item['icon']} {item['label']}",
        )
        st.session_state.active_filters = [item["id"] for item in selected_labels]

        if st.session_state.active_tab == "assets":
            render_assets_tab(filtered_assets)
        elif st.session_state.active_tab == "routes":
            render_routes_tab()
        elif st.session_state.active_tab == "pgis":
            render_pgis_tab()
        elif st.session_state.active_tab == "about":
            render_about_tab()


def main():
    inject_css()
    st.session_state.setdefault("active_filters", [])
    st.session_state.setdefault("active_route", None)
    st.session_state.setdefault("active_tab", "assets")
    st.session_state.setdefault("selected_asset_id", ASSETS[0]["id"])
    st.session_state.setdefault("demo_submissions", [])

    filtered_assets = (
        ASSETS if not st.session_state.active_filters else [asset for asset in ASSETS if asset["type"] in st.session_state.active_filters]
    )
    render_sidebar(filtered_assets)

    map_col, detail_col = st.columns([3.2, 1.05], gap="medium")
    with map_col:
        overlay_col1, overlay_col2, overlay_col3 = st.columns([1.0, 0.95, 1.35])
        with overlay_col1:
            st.markdown(
                f"""
                <div class="pgis-panel">
                  <h4><span class="dot"></span> PGIS 실시간 참여</h4>
                  <div style="font-size:11px;color:var(--text2);line-height:1.6">주민·이용자가 직접 남산의 장소 자산을 발굴하고 지도화합니다</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with overlay_col2:
            st.markdown(
                """
                <div class="stats-bar">
                  <div class="stat-item"><div class="stat-value">18</div><div class="stat-label">등록 자산</div></div>
                  <div class="stat-item"><div class="stat-value">5</div><div class="stat-label">보행 루트</div></div>
                  <div class="stat-item"><div class="stat-value">6</div><div class="stat-label">대상 권역</div></div>
                  <div class="stat-item"><div class="stat-value">5.2km²</div><div class="stat-label">대상 면적</div></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with overlay_col3:
            legend = "".join(
                f'<div class="legend-item"><div class="legend-picture" style="background:{item["bg"]};color:{item["color"]}">{item["icon"]}</div><span class="legend-label">{item["label"]}</span></div>'
                for item in ASSET_TYPES
            )
            legend = f'<div class="legend-grid">{legend}</div>'
            st.markdown(f'<div class="legend"><h4>자산 유형 범례</h4>{legend}</div>', unsafe_allow_html=True)

        fmap = make_map(filtered_assets, st.session_state.active_route)
        state = st_folium(fmap, height=730, use_container_width=True, returned_objects=["last_object_clicked"])
        sync_clicked_asset(state)

    with detail_col:
        asset = ASSET_BY_ID.get(st.session_state.selected_asset_id, ASSETS[0])
        render_detail(asset)


if __name__ == "__main__":
    main()
