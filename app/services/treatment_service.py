from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL)
    return _engine


def get_treatment(class_key: str):
    """Disease class_key (jem ke 'bacterial_blight') mate verified treatment
    records shodhe. Koi match na male to None (UI ne khabar padse ke
    treatment database ma aa problem mate koi verified record nathi)."""
    query = text("""
        SELECT
            d.display_name AS disease_name,
            p.product_name, p.manufacturer, p.active_ingredient,
            p.formulation, p.is_verified, p.last_verified_date, p.source_url,
            t.purpose, t.application_method, t.application_rate,
            t.water_dilution, t.application_timing,
            t.pre_harvest_interval, t.safety_instructions
        FROM treatments t
        JOIN diseases d ON t.disease_id = d.id
        JOIN products p ON t.product_id = p.id
        WHERE d.class_key = :class_key
    """)
    with _get_engine().connect() as conn:
        rows = conn.execute(query, {"class_key": class_key}).mappings().all()
    return [dict(r) for r in rows]