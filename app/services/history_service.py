from datetime import date
from sqlalchemy import create_engine, text
from config.settings import DATABASE_URL

_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL)
    return _engine


def get_or_create_user(name: str, phone: str = None, location: str = None) -> int:
    with _get_engine().begin() as conn:
        if phone:
            row = conn.execute(
                text("SELECT id FROM users WHERE phone = :phone"), {"phone": phone}
            ).fetchone()
            if row:
                return row[0]
        result = conn.execute(
            text("INSERT INTO users (name, phone, location) VALUES (:name, :phone, :location)"),
            {"name": name, "phone": phone, "location": location},
        )
        return result.lastrowid


def get_user_farms(user_id: int):
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("SELECT id, farm_name, location, area_acres, soil_type FROM farms WHERE user_id = :uid"),
            {"uid": user_id},
        ).mappings().all()
    return [dict(r) for r in rows]


def create_farm(user_id: int, farm_name: str, location: str = None, area_acres: float = None, soil_type: str = None) -> int:
    with _get_engine().begin() as conn:
        result = conn.execute(
            text("""INSERT INTO farms (user_id, farm_name, location, area_acres, soil_type)
                    VALUES (:uid, :name, :loc, :area, :soil)"""),
            {"uid": user_id, "name": farm_name, "loc": location, "area": area_acres, "soil": soil_type},
        )
        return result.lastrowid


def save_record(farm_id: int, record_type: str, **kwargs):
    """record_type: 'crop_recommendation' | 'plant_analysis' | 'soil_analysis'"""
    with _get_engine().begin() as conn:
        conn.execute(
            text("""INSERT INTO crop_history
                    (farm_id, record_type, crop, predicted_class, confidence, severity,
                     n_value, p_value, k_value, ph_value, summary, image_path)
                    VALUES (:farm_id, :record_type, :crop, :predicted_class, :confidence, :severity,
                            :n_value, :p_value, :k_value, :ph_value, :summary, :image_path)"""),
            {
                "farm_id": farm_id,
                "record_type": record_type,
                "crop": kwargs.get("crop"),
                "predicted_class": kwargs.get("predicted_class"),
                "confidence": kwargs.get("confidence"),
                "severity": kwargs.get("severity"),
                "n_value": kwargs.get("n_value"),
                "p_value": kwargs.get("p_value"),
                "k_value": kwargs.get("k_value"),
                "ph_value": kwargs.get("ph_value"),
                "summary": kwargs.get("summary"),
                "image_path": kwargs.get("image_path"),
            },
        )


def get_farm_history(farm_id: int, limit: int = 20):
    with _get_engine().connect() as conn:
        rows = conn.execute(
            text("""SELECT * FROM crop_history WHERE farm_id = :fid
                    ORDER BY created_at DESC LIMIT :limit"""),
            {"fid": farm_id, "limit": limit},
        ).mappings().all()
    return [dict(r) for r in rows]