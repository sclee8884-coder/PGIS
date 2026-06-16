import html
import json
import os
import re
import urllib.error
import urllib.request
import uuid

import folium
import psycopg2
from psycopg2 import sql
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
ROUTE_ASSET_BY_ID = {item["id"]: item for item in ASSETS}
JUNG_GU_BOUNDS = [[37.5380, 126.9650], [37.5710, 127.0250]]
JUNG_GU_CENTER = [37.5636, 126.9976]


def is_within_jung_gu_bounds(points):
    min_lat, min_lng = JUNG_GU_BOUNDS[0]
    max_lat, max_lng = JUNG_GU_BOUNDS[1]
    return all(min_lat <= lat <= max_lat and min_lng <= lng <= max_lng for lat, lng in points)


def get_config_value(key, default=""):
    value = os.environ.get(key)
    if value is not None:
        return value
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def get_database_url():
    return get_config_value("DATABASE_URL", "").strip()


def normalize_asset_type(value):
    value = (value or "").strip()
    if "역사" in value or "유산" in value:
        return "history"
    if "생활" in value or "시장" in value:
        return "life"
    if "문화" in value or "시설" in value:
        return "culture"
    if "생태" in value or "자연" in value or "녹지" in value:
        return "ecology"
    if "경관" in value or "조망" in value:
        return "landscape"
    return value if value in TYPE_BY_ID else "community"


def normalize_tags(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except json.JSONDecodeError:
            pass
        return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value).strip()]


def pg_identifier(value):
    parts = [part.strip() for part in str(value).split(".") if part.strip()]
    return sql.Identifier(*parts)


def pg_table_parts(table_name):
    parts = [part.strip() for part in str(table_name).split(".") if part.strip()]
    if len(parts) >= 2:
        return parts[-2], parts[-1]
    return None, parts[0]


def text_column_expr(column_name, available_columns, default):
    if column_name in available_columns:
        return sql.SQL("COALESCE({column}::text, {default})").format(
            column=pg_identifier(column_name),
            default=sql.Literal(default),
        )
    return sql.Literal(default)


def id_column_expr(column_name, available_columns):
    if column_name in available_columns:
        return sql.SQL("{column}::text").format(column=pg_identifier(column_name))
    return sql.SQL("ROW_NUMBER() OVER ()::text")


def first_existing_column(available_columns, candidates):
    for candidate in candidates:
        if candidate and candidate in available_columns:
            return candidate
    return None


def read_table_columns(cur, table_name):
    schema_name, plain_table_name = pg_table_parts(table_name)
    if schema_name:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            """,
            (schema_name, plain_table_name),
        )
    else:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            """,
            (plain_table_name,),
        )
    return {row[0] for row in cur.fetchall()}


def read_table_column_types(cur, table_name):
    schema_name, plain_table_name = pg_table_parts(table_name)
    if schema_name:
        cur.execute(
            """
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            """,
            (schema_name, plain_table_name),
        )
    else:
        cur.execute(
            """
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = %s
            """,
            (plain_table_name,),
        )
    return {row[0]: {"data_type": row[1], "udt_name": row[2]} for row in cur.fetchall()}


def discover_geometry_table(cur, preferred_geom_column):
    cur.execute(
        """
        SELECT f_table_schema, f_table_name, f_geometry_column
        FROM geometry_columns
        WHERE f_table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY
            CASE WHEN f_geometry_column = %s THEN 0 ELSE 1 END,
            f_table_schema,
            f_table_name
        LIMIT 1
        """,
        (preferred_geom_column,),
    )
    row = cur.fetchone()
    if not row:
        return None, None
    schema_name, table_name, geom_column = row
    return f"{schema_name}.{table_name}", geom_column


def ensure_default_pgis_table(cur, table_name, geom_column):
    cur.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    cur.execute(
        sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {table} (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                zone TEXT,
                description TEXT,
                tags TEXT,
                route_ids TEXT,
                source TEXT,
                {geom_column} geometry(Point, 4326) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT now()
            )
            """
        ).format(
            table=pg_identifier(table_name),
            geom_column=pg_identifier(geom_column),
        )
    )
    schema_name, plain_table_name = pg_table_parts(table_name)
    index_prefix = f"{plain_table_name}_{geom_column}".replace(".", "_")
    cur.execute(
        sql.SQL("CREATE INDEX IF NOT EXISTS {index_name} ON {table} USING GIST ({geom_column})").format(
            index_name=pg_identifier(f"{index_prefix}_idx"),
            table=pg_identifier(table_name),
            geom_column=pg_identifier(geom_column),
        )
    )
    cur.execute(
        sql.SQL("CREATE INDEX IF NOT EXISTS {index_name} ON {table} (type)").format(
            index_name=pg_identifier(f"{plain_table_name}_type_idx"),
            table=pg_identifier(table_name),
        )
    )


def can_insert_text_id(column_meta):
    if not column_meta:
        return False
    return column_meta["data_type"] in {"text", "character varying", "character", "uuid"}


def save_pgis_asset_to_database(asset, route_ids, source):
    database_url = get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL이 설정되어 있지 않습니다.")

    table_name = get_config_value("PGIS_TABLE", "pgis_assets")
    geom_column = get_config_value("PGIS_GEOM_COLUMN", "geom")
    id_column = get_config_value("PGIS_ID_COLUMN", "id")
    name_column = get_config_value("PGIS_NAME_COLUMN", "name")
    type_column = get_config_value("PGIS_TYPE_COLUMN", "type")
    zone_column = get_config_value("PGIS_ZONE_COLUMN", "zone")
    desc_column = get_config_value("PGIS_DESC_COLUMN", "description")
    tags_column = get_config_value("PGIS_TAGS_COLUMN", "tags")

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            ensure_default_pgis_table(cur, table_name, geom_column)
            column_types = read_table_column_types(cur, table_name)
            available_columns = set(column_types)

            insert_columns = []
            value_exprs = []
            values = []
            saved_asset_id = asset["id"]

            if id_column in available_columns and can_insert_text_id(column_types[id_column]):
                insert_columns.append(pg_identifier(id_column))
                value_exprs.append(sql.Placeholder())
                if column_types[id_column]["data_type"] == "uuid":
                    saved_asset_id = str(uuid.uuid4())
                    values.append(saved_asset_id)
                else:
                    values.append(asset["id"])

            column_values = [
                (name_column, asset["name"]),
                (type_column, asset["type"]),
                (zone_column, asset["zone"]),
                (desc_column, asset["desc"]),
                (tags_column, json.dumps(asset["tags"], ensure_ascii=False)),
                ("route_ids", json.dumps(route_ids, ensure_ascii=False)),
                ("source", source),
            ]
            for column_name, value in column_values:
                if column_name in available_columns:
                    insert_columns.append(pg_identifier(column_name))
                    value_exprs.append(sql.Placeholder())
                    values.append(value)

            if geom_column not in available_columns:
                raise ValueError(f"`{geom_column}` geometry 컬럼을 찾을 수 없습니다.")
            insert_columns.append(pg_identifier(geom_column))
            value_exprs.append(sql.SQL("ST_SetSRID(ST_MakePoint(%s, %s), 4326)"))
            values.extend([asset["lng"], asset["lat"]])

            if not insert_columns:
                raise ValueError("저장할 수 있는 컬럼을 찾지 못했습니다.")

            query = sql.SQL("INSERT INTO {table} ({columns}) VALUES ({values})").format(
                table=pg_identifier(table_name),
                columns=sql.SQL(", ").join(insert_columns),
                values=sql.SQL(", ").join(value_exprs),
            )
            cur.execute(query, values)

    load_postgis_assets.clear()
    return saved_asset_id


def delete_pgis_asset_from_database(asset_id):
    database_url = get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL이 설정되어 있지 않습니다.")

    table_name = get_config_value("PGIS_TABLE", "pgis_assets")
    geom_column = get_config_value("PGIS_GEOM_COLUMN", "geom")
    id_column = get_config_value("PGIS_ID_COLUMN", "id")

    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            ensure_default_pgis_table(cur, table_name, geom_column)
            available_columns = read_table_columns(cur, table_name)
            if id_column not in available_columns:
                raise ValueError(f"`{id_column}` ID 컬럼을 찾을 수 없습니다.")

            query = sql.SQL("DELETE FROM {table} WHERE {id_column}::text = %s").format(
                table=pg_identifier(table_name),
                id_column=pg_identifier(id_column),
            )
            cur.execute(query, (str(asset_id),))
            deleted_count = cur.rowcount

    load_postgis_assets.clear()
    if deleted_count == 0:
        raise ValueError("해당 ID의 데이터가 DB에 없습니다. 샘플 데이터는 삭제할 수 없습니다.")
    return deleted_count


def ensure_pgis_database_schema(database_url, table_name, geom_column):
    if not database_url:
        return
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            ensure_default_pgis_table(cur, table_name, geom_column)


@st.cache_data(ttl=300, show_spinner=False)
def load_postgis_assets(
    database_url,
    table_name,
    geom_column,
    id_column,
    name_column,
    type_column,
    zone_column,
    desc_column,
    tags_column,
):
    if not database_url:
        return []

    assets = []
    with psycopg2.connect(database_url) as conn:
        with conn.cursor() as cur:
            available_columns = read_table_columns(cur, table_name)
            if geom_column not in available_columns:
                discovered_table, discovered_geom = discover_geometry_table(cur, geom_column)
                if not discovered_table:
                    raise ValueError(f"`{geom_column}` geometry 컬럼을 찾지 못했습니다.")
                table_name = discovered_table
                geom_column = discovered_geom
                available_columns = read_table_columns(cur, table_name)

            actual_name_column = first_existing_column(
                available_columns,
                [name_column, "문화시설명", "미래유산명", "name", "이름", "명칭"],
            )
            actual_type_column = first_existing_column(
                available_columns,
                [type_column, "주제분류", "유형 1", "유형", "분야", "category"],
            )
            actual_zone_column = first_existing_column(
                available_columns,
                [zone_column, "자치구", "지역", "주소", "소재지", "zone"],
            )
            actual_desc_column = first_existing_column(
                available_columns,
                [desc_column, "설명문", "시설소개", "기타사항", "description", "desc"],
            )
            actual_tags_column = first_existing_column(
                available_columns,
                [tags_column, "주제분류", "분야", "유형 1", "tags"],
            )

            query = sql.SQL(
                """
                SELECT
                    {id_expr} AS id,
                    {name_expr} AS name,
                    {type_expr} AS type,
                    {zone_expr} AS zone,
                    {desc_expr} AS desc,
                    {tags_expr} AS tags,
                    ST_Y(ST_Transform(ST_Centroid({geom_col}), 4326)) AS lat,
                    ST_X(ST_Transform(ST_Centroid({geom_col}), 4326)) AS lng,
                    ST_AsGeoJSON(ST_Transform({geom_col}, 4326)) AS geometry
                FROM {table}
                WHERE {geom_col} IS NOT NULL
                """
            ).format(
                table=pg_identifier(table_name),
                geom_col=pg_identifier(geom_column),
                id_expr=id_column_expr(id_column, available_columns),
                name_expr=text_column_expr(actual_name_column, available_columns, "이름 없음"),
                type_expr=text_column_expr(actual_type_column, available_columns, "community"),
                zone_expr=text_column_expr(actual_zone_column, available_columns, "미분류"),
                desc_expr=text_column_expr(actual_desc_column, available_columns, ""),
                tags_expr=text_column_expr(actual_tags_column, available_columns, ""),
            )
            cur.execute(query)
            for row in cur.fetchall():
                asset_id, name, asset_type, zone, desc, tags, lat, lng, geometry = row
                if lat is None or lng is None:
                    continue
                assets.append(
                    {
                        "id": asset_id,
                        "name": name,
                        "type": normalize_asset_type(asset_type),
                        "zone": zone or "미분류",
                        "desc": desc or "",
                        "tags": normalize_tags(tags),
                        "lat": float(lat),
                        "lng": float(lng),
                        "geometry": json.loads(geometry) if geometry else None,
                    }
                )
    return assets


def load_assets():
    database_url = get_database_url()
    if not database_url:
        return ASSETS, None

    table_name = get_config_value("PGIS_TABLE", "pgis_assets")
    geom_column = get_config_value("PGIS_GEOM_COLUMN", "geom")
    id_column = get_config_value("PGIS_ID_COLUMN", "id")
    name_column = get_config_value("PGIS_NAME_COLUMN", "name")
    type_column = get_config_value("PGIS_TYPE_COLUMN", "type")
    zone_column = get_config_value("PGIS_ZONE_COLUMN", "zone")
    desc_column = get_config_value("PGIS_DESC_COLUMN", "description")
    tags_column = get_config_value("PGIS_TAGS_COLUMN", "tags")

    try:
        ensure_pgis_database_schema(database_url, table_name, geom_column)
        assets = load_postgis_assets(
            database_url,
            table_name,
            geom_column,
            id_column,
            name_column,
            type_column,
            zone_column,
            desc_column,
            tags_column,
        )
    except Exception as exc:
        return ASSETS, f"PostGIS 데이터를 불러오지 못해 샘플 데이터를 표시합니다: {exc}"

    if not assets:
        return ASSETS, f"INFO: PostGIS 테이블 `{table_name}`은 준비됐지만 아직 등록된 PGIS 자산이 없어 샘플 데이터를 표시합니다."
    return assets, None


def merge_session_assets(base_assets):
    return base_assets + st.session_state.get("demo_submissions", [])


def next_demo_asset_id():
    return f"pgis-{len(st.session_state.get('demo_submissions', [])) + 1}"


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
        .legend-title {font-size:13px;font-weight:700;margin:0 0 12px;color:var(--accent);}
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
        .pgis-form-shell {
          background:linear-gradient(180deg,#ffffff 0%,#f8fafc 100%);
          border:1px solid var(--border);border-radius:12px;padding:18px;
          box-shadow:0 10px 28px rgba(15,23,42,.08);
        }
        .pgis-form-hero {
          border-radius:10px;padding:16px;margin-bottom:14px;
          background:linear-gradient(135deg,rgba(15,118,110,.10),rgba(244,114,182,.12));
          border:1px solid rgba(15,118,110,.16);
        }
        .pgis-form-kicker {font-size:11px;font-weight:700;color:var(--accent);margin-bottom:6px;}
        .pgis-form-title {font-size:20px;font-weight:800;color:var(--text);line-height:1.25;margin-bottom:6px;}
        .pgis-form-copy {font-size:12px;line-height:1.6;color:var(--text2);}
        .pgis-section {
          display:flex;align-items:center;gap:8px;margin:16px 0 8px;
          color:var(--accent);font-size:13px;font-weight:800;
        }
        .pgis-section span {
          width:22px;height:22px;border-radius:7px;background:rgba(15,118,110,.10);
          display:flex;align-items:center;justify-content:center;font-size:11px;
        }
        .pgis-note {
          padding:10px 12px;border-radius:8px;background:#ecfeff;border:1px solid #bae6fd;
          color:#155e75;font-size:11px;line-height:1.6;margin:12px 0;
        }
        .danger-zone {
          margin-top:18px;padding:12px;border-radius:10px;background:#fff7ed;
          border:1px solid #fed7aa;color:#9a3412;font-size:12px;line-height:1.6;
        }
        .danger-title {font-size:13px;font-weight:800;color:#c2410c;margin-bottom:4px;}
        .pgis-mini-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin:10px 0 4px;}
        .pgis-mini-type {border:1px solid var(--border);border-radius:8px;padding:8px 6px;background:#fff;text-align:center;font-size:10px;color:var(--text2);}
        .pgis-mini-type strong {display:block;font-size:15px;color:var(--accent);line-height:1;margin-bottom:4px;}
        div[data-testid="stForm"] {
          border:0;padding:0;background:transparent;
        }
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


def clean_display_text(value):
    text = html.unescape(str(value or ""))
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"(^|\s)[#*_`~]+", " ", text)
    text = re.sub(r"[#*_`~]+($|\s)", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def truncate_text(value, limit=80):
    text = clean_display_text(value)
    return text if len(text) <= limit else f"{text[:limit]}..."


def render_asset_card(asset):
    asset_type = TYPE_BY_ID[asset["type"]]
    tags = "".join(f'<span class="card-tag">{esc(tag)}</span>' for tag in asset["tags"])
    desc = truncate_text(asset["desc"])
    return f"""
    <div class="card">
      <div class="card-header">
        <div class="card-icon asset-{asset['type']}">{asset_type['icon']}</div>
        <div><div class="card-title">{esc(asset['name'])}</div><div class="card-sub">{esc(asset['zone'])}</div></div>
      </div>
      <div class="card-desc">{esc(desc)}</div>
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
    desc = truncate_text(asset["desc"])
    tags = "".join(
        f"<span style='font-size:10px;padding:2px 8px;border-radius:12px;background:{asset_type['bg']};color:{asset_type['color']}'>{esc(tag)}</span>"
        for tag in asset["tags"]
    )
    return f"""
    <div style="min-width:180px">
      <div style="font-size:14px;font-weight:600;margin-bottom:4px">{asset_type['icon']} {esc(asset['name'])}</div>
      <div style="font-size:11px;color:#64748b;margin-bottom:8px">{esc(asset['zone'])}</div>
      <div style="font-size:12px;line-height:1.6;color:#0f172a">{esc(desc)}</div>
      <div style="margin-top:8px;display:flex;gap:4px;flex-wrap:wrap">{tags}</div>
    </div>
    """


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_route_path(route_id, point_ids):
    waypoints = []
    for pid in point_ids:
        waypoint = ASSET_BY_ID.get(pid) or ASSET_BY_ID.get(str(pid)) or ROUTE_ASSET_BY_ID.get(pid)
        if waypoint:
            waypoints.append(waypoint)
    if len(waypoints) < 2:
        return []

    coords = ";".join(f"{item['lng']},{item['lat']}" for item in waypoints)
    url = (
        "https://routing.openstreetmap.de/routed-foot/route/v1/foot/"
        f"{coords}?overview=full&geometries=geojson&steps=false"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return [[item["lat"], item["lng"]] for item in waypoints]

    if payload.get("code") != "Ok" or not payload.get("routes"):
        return [[item["lat"], item["lng"]] for item in waypoints]

    geometry = payload["routes"][0].get("geometry", {})
    coordinates = geometry.get("coordinates", [])
    return [[lat, lng] for lng, lat in coordinates] or [[item["lat"], item["lng"]] for item in waypoints]


def route_path(route):
    return fetch_route_path(route["id"], tuple(route["points"]))


def make_map(filtered_assets, active_route):
    route = next((item for item in ROUTES if item["id"] == active_route), None)
    visible_assets = [
        asset for asset in filtered_assets if is_within_jung_gu_bounds([(asset["lat"], asset["lng"])])
    ]
    center = JUNG_GU_CENTER
    zoom = 15
    if route:
        path = route_path(route)
        if path:
            route_center = [sum(p[0] for p in path) / len(path), sum(p[1] for p in path) / len(path)]
            center = route_center if is_within_jung_gu_bounds([route_center]) else JUNG_GU_CENTER
            zoom = 14

    fmap = folium.Map(
        location=center,
        zoom_start=zoom,
        zoom_control=False,
        tiles=None,
        control_scale=True,
        min_lat=JUNG_GU_BOUNDS[0][0],
        max_lat=JUNG_GU_BOUNDS[1][0],
        min_lon=JUNG_GU_BOUNDS[0][1],
        max_lon=JUNG_GU_BOUNDS[1][1],
        max_bounds=True,
    )
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="&copy; CARTO",
        max_zoom=19,
        name="CartoDB Positron",
    ).add_to(fmap)
    plugins.Fullscreen(position="topright").add_to(fmap)
    plugins.MiniMap(toggle_display=True, position="bottomleft").add_to(fmap)

    marker_cluster = plugins.MarkerCluster(
        name="자산 클러스터",
        options={"showCoverageOnHover": False, "spiderfyOnMaxZoom": True},
    ).add_to(fmap)
    for asset in visible_assets:
        folium.Marker(
            location=[asset["lat"], asset["lng"]],
            popup=folium.Popup(popup_html(asset), max_width=260),
            tooltip=asset["name"],
            icon=folium.DivIcon(html=marker_html(asset), icon_size=(32, 32), icon_anchor=(16, 16)),
        ).add_to(marker_cluster)

    if route:
        path = route_path(route)
        if len(path) > 1:
            folium.PolyLine(path, color=route["color"], weight=4, opacity=0.85, dash_array="10,6").add_to(fmap)
            if is_within_jung_gu_bounds(path):
                fmap.fit_bounds(path, padding=(60, 60))
            else:
                fmap.fit_bounds(JUNG_GU_BOUNDS, padding=(20, 20))
    else:
        fmap.fit_bounds(JUNG_GU_BOUNDS, padding=(20, 20))
    return fmap


def sync_clicked_asset(map_state, assets):
    clicked = map_state.get("last_object_clicked") if map_state else None
    if not clicked:
        return
    lat = round(clicked.get("lat", 0), 4)
    lng = round(clicked.get("lng", 0), 4)
    for asset in assets:
        if round(asset["lat"], 4) == lat and round(asset["lng"], 4) == lng:
            st.session_state.selected_asset_id = asset["id"]
            break


def render_detail(asset):
    asset_type = TYPE_BY_ID[asset["type"]]
    desc = clean_display_text(asset["desc"])
    route_ids = set(asset.get("route_ids", []))
    route_matches = [route for route in ROUTES if asset["id"] in route["points"] or route["id"] in route_ids]
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
          <p>{esc(desc)}</p>
          <div style="margin:18px 0 8px;color:var(--accent);font-size:14px;font-weight:600">태그</div>
          <div class="card-tags">{tags}</div>
          <div style="margin:18px 0 8px;color:var(--accent);font-size:14px;font-weight:600">연결 루트</div>
          {routes}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="danger-zone">
          <div class="danger-title">데이터 삭제</div>
          선택한 자산을 데이터베이스에서 삭제합니다. 삭제 후 지도와 목록에서 사라집니다.
        </div>
        """,
        unsafe_allow_html=True,
    )
    confirm_delete = st.checkbox("이 자산을 삭제하겠습니다.", key=f"confirm_delete_{asset['id']}")
    if st.button("선택 자산 삭제", key=f"delete_asset_{asset['id']}", disabled=not confirm_delete, use_container_width=True):
        try:
            delete_pgis_asset_from_database(asset["id"])
        except Exception as exc:
            st.error(f"삭제에 실패했습니다: {exc}")
        else:
            st.session_state.selected_asset_id = None
            st.session_state.delete_flash = True
            st.rerun()


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
        """
        <div class="pgis-form-shell">
          <div class="pgis-form-hero">
            <div class="pgis-form-kicker">PGIS DATA ENTRY</div>
            <div class="pgis-form-title">장소 정보를 지도 자산으로 등록</div>
            <div class="pgis-form-copy">스크린샷의 상세 카드에 들어갈 이름, 유형, 위치, 설명, 태그와 연결 루트를 한 번에 입력합니다.</div>
          </div>
          <div class="pgis-mini-grid">
            <div class="pgis-mini-type"><strong>文</strong>유형</div>
            <div class="pgis-mini-type"><strong>37</strong>좌표</div>
            <div class="pgis-mini-type"><strong>#</strong>태그</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.pop("pgis_flash", False):
        st.success("장소가 등록되었습니다. 지도와 상세 카드에서 바로 확인할 수 있습니다.")

    with st.form("pgis_form", clear_on_submit=True):
        st.markdown('<div class="pgis-section"><span>1</span>기본 정보</div>', unsafe_allow_html=True)
        name = st.text_input("자산명 *", placeholder="예: 국립극장")
        asset_type = st.selectbox("자산 유형 *", ASSET_TYPES, index=2, format_func=lambda item: f"{item['icon']} {item['label']}")
        zone = st.selectbox("위치/권역 *", ZONES, format_func=lambda item: item["name"])

        st.markdown('<div class="pgis-section"><span>2</span>지도 위치</div>', unsafe_allow_html=True)
        coord_cols = st.columns(2)
        with coord_cols[0]:
            lat = st.number_input("위도 *", min_value=37.5380, max_value=37.5710, value=37.5530, step=0.0001, format="%.4f")
        with coord_cols[1]:
            lng = st.number_input("경도 *", min_value=126.9650, max_value=127.0250, value=127.0045, step=0.0001, format="%.4f")

        st.markdown('<div class="pgis-section"><span>3</span>설명과 연결</div>', unsafe_allow_html=True)
        desc = st.text_area(
            "설명 본문",
            height=180,
            placeholder="설립 시기, 장소의 의미, 규모, 현재 활용, 주민 기억 등을 입력하세요.",
        )
        tags = st.text_input("태그", placeholder="예: 공연장, 공연예술, 국립문화시설")
        route_selection = st.multiselect("연결 루트", ROUTES, format_func=lambda route: route["name"])
        contributor = st.text_input("제보자/출처", placeholder="예: 주민 워크숍, 현장조사, 문헌자료")

        st.markdown(
            '<div class="pgis-note">현재 세션의 데모 자산으로 저장됩니다. PostGIS 연결 전 화면 구성과 필드 검증에 바로 사용할 수 있습니다.</div>',
            unsafe_allow_html=True,
        )
        submitted = st.form_submit_button("지도에 등록하기", type="primary", use_container_width=True)
        if submitted:
            if name.strip():
                asset_id = f"pgis-{uuid.uuid4().hex[:12]}"
                submitted_tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
                if contributor.strip():
                    submitted_tags.append(contributor.strip())
                route_ids = [route["id"] for route in route_selection]
                asset = {
                    "id": asset_id,
                    "name": name.strip(),
                    "type": asset_type["id"],
                    "lat": float(lat),
                    "lng": float(lng),
                    "zone": zone["name"],
                    "desc": desc.strip() or "아직 설명이 입력되지 않았습니다.",
                    "tags": submitted_tags,
                    "route_ids": route_ids,
                }
                try:
                    saved_asset_id = save_pgis_asset_to_database(asset, route_ids, contributor.strip())
                except Exception as exc:
                    st.error(f"데이터베이스 저장에 실패했습니다: {exc}")
                else:
                    st.session_state.selected_asset_id = saved_asset_id
                    st.session_state.pending_clear_filters = True
                    st.session_state.pgis_flash = True
                    st.rerun()
            else:
                st.warning("자산명을 입력해주세요.")

    if st.session_state.demo_submissions:
        st.markdown("#### 방금 등록한 데이터")
        for asset in reversed(st.session_state.demo_submissions[-3:]):
            st.markdown(render_asset_card(asset), unsafe_allow_html=True)
            if st.button("상세 카드로 보기", key=f"pgis_preview_{asset['id']}", use_container_width=True):
                st.session_state.selected_asset_id = asset["id"]
                st.rerun()

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
        if st.button("PGIS 입력 열기", key="open_pgis_panel", use_container_width=True):
            st.session_state.right_panel_mode = "PGIS 입력"
            st.rerun()

        selected_labels = st.multiselect(
            "자산 유형 필터",
            ASSET_TYPES,
            key="asset_filter_selection",
            format_func=lambda item: f"{item['icon']} {item['label']}",
        )
        st.session_state.active_filters = [item["id"] for item in selected_labels]

        if st.session_state.active_tab == "assets":
            render_assets_tab(filtered_assets)
        elif st.session_state.active_tab == "routes":
            render_routes_tab()
        elif st.session_state.active_tab == "pgis":
            st.markdown(
                '<div class="about-text">오른쪽 패널에서 PGIS 장소 데이터를 입력하고 지도에 바로 반영합니다.</div>',
                unsafe_allow_html=True,
            )
        elif st.session_state.active_tab == "about":
            render_about_tab()


def main():
    global ASSET_BY_ID

    inject_css()
    st.session_state.setdefault("demo_submissions", [])
    assets, data_warning = load_assets()
    assets = merge_session_assets(assets)
    asset_by_id = {item["id"]: item for item in assets}
    ASSET_BY_ID = asset_by_id

    st.session_state.setdefault("active_filters", [])
    st.session_state.setdefault("asset_filter_selection", [TYPE_BY_ID[item] for item in st.session_state.active_filters])
    st.session_state.setdefault("active_route", None)
    st.session_state.setdefault("active_tab", "assets")
    st.session_state.setdefault("selected_asset_id", assets[0]["id"])
    pending_legend_filter = st.session_state.pop("pending_legend_filter", None)
    if pending_legend_filter in TYPE_BY_ID:
        st.session_state.active_filters = [pending_legend_filter]
        st.session_state.asset_filter_selection = [TYPE_BY_ID[pending_legend_filter]]
        st.session_state.active_tab = "assets"
    if st.session_state.pop("pending_clear_filters", False):
        st.session_state.active_filters = []
        st.session_state.asset_filter_selection = []
    if st.session_state.selected_asset_id is None:
        st.session_state.selected_asset_id = assets[0]["id"]
    if st.session_state.selected_asset_id not in asset_by_id:
        st.session_state.selected_asset_id = assets[0]["id"]

    filtered_assets = (
        assets if not st.session_state.active_filters else [asset for asset in assets if asset["type"] in st.session_state.active_filters]
    )
    render_sidebar(filtered_assets)
    if data_warning:
        if data_warning.startswith("INFO: "):
            st.info(data_warning.replace("INFO: ", "", 1))
        else:
            st.warning(data_warning)
    if st.session_state.pop("delete_flash", False):
        st.success("선택한 자산을 데이터베이스에서 삭제했습니다.")

    show_pgis_panel = st.session_state.active_tab == "pgis" or st.session_state.get("right_panel_mode") == "PGIS 입력"
    column_ratio = [2.35, 1.45] if show_pgis_panel else [3.2, 1.05]
    map_col, detail_col = st.columns(column_ratio, gap="medium")
    with map_col:
        _, legend_col = st.columns([2.25, 1.35])
        with legend_col:
            with st.container(border=True):
                st.markdown('<div class="legend-title">자산 유형 범례</div>', unsafe_allow_html=True)
                for row_start in range(0, len(ASSET_TYPES), 3):
                    legend_cols = st.columns(3)
                    for col, item in zip(legend_cols, ASSET_TYPES[row_start : row_start + 3]):
                        active = item["id"] in st.session_state.active_filters
                        label = f"{item['icon']} {item['label']}"
                        with col:
                            if st.button(label, key=f"legend_{item['id']}", type="primary" if active else "secondary", use_container_width=True):
                                st.session_state.pending_legend_filter = item["id"]
                                st.rerun()

        fmap = make_map(filtered_assets, st.session_state.active_route)
        state = st_folium(fmap, height=730, use_container_width=True, returned_objects=["last_object_clicked"])
        sync_clicked_asset(state, assets)

    with detail_col:
        if st.session_state.active_tab == "pgis":
            st.markdown('<div class="type-badge" style="background:rgba(15,118,110,.10);color:var(--accent)">PGIS 입력 모드</div>', unsafe_allow_html=True)
            render_pgis_tab()
        else:
            panel_mode = st.radio(
                "오른쪽 패널",
                ["상세 정보", "PGIS 입력"],
                horizontal=True,
                label_visibility="collapsed",
                key="right_panel_mode",
            )
            if panel_mode == "PGIS 입력":
                render_pgis_tab()
            else:
                asset = asset_by_id.get(st.session_state.selected_asset_id, assets[0])
                render_detail(asset)


if __name__ == "__main__":
    main()
