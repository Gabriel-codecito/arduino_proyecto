import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

from django.conf import settings

ML_DIR = os.path.join(settings.BASE_DIR, 'ml_models')
TARIFA_DEFAULT = 150   # CLP por kWh — ajusta según tu proveedor


def _cargar_modelo():
    """Carga el modelo, scaler, features y config desde ml_models/."""
    try:
        modelo   = joblib.load(os.path.join(ML_DIR, 'modelo_energia.pkl'))
        scaler   = joblib.load(os.path.join(ML_DIR, 'scaler.pkl'))
        features = joblib.load(os.path.join(ML_DIR, 'features.pkl'))
        config   = joblib.load(os.path.join(ML_DIR, 'config.pkl'))
        return modelo, scaler, features, config
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f'Modelo no encontrado ({e}). '
            'Ejecuta: python manage.py train_model'
        )


def predecir_consumo_y_costo(dias: int = 30, potencia_prom: float = None,
                              kwh_historico: list = None) -> list:
    """
    Genera predicciones diarias de kWh y costo CLP.

    Parámetros
    ----------
    dias            : int   → cantidad de días a predecir (1–90)
    potencia_prom   : float → potencia promedio reciente en W (opcional)
    kwh_historico   : list  → lista de kWh diarios históricos (opcional)

    Retorna
    -------
    list de dicts:
        [{'fecha': '2025-01-20', 'kwh': 12.34, 'costo': 1851}, ...]
    """
    dias = max(1, min(int(dias), 90))

    modelo, scaler, features, config = _cargar_modelo()
    tarifa = config.get('tarifa', TARIFA_DEFAULT)

    # ── Historial de kWh (para calcular los lag features) ──────────
    if kwh_historico is None or len(kwh_historico) == 0:
        # Fallback: importar aquí para evitar import circular
        kwh_historico = _obtener_kwh_historico_bd()

    if potencia_prom is None:
        potencia_prom = _obtener_potencia_prom_bd()

    kwh_serie = list(kwh_historico)   # copia mutable

    # ── Predicción iterativa día a día ──────────────────────────────
    hoy        = datetime.now().date()
    resultados = []

    for i in range(1, dias + 1):
        fecha_pred = hoy + timedelta(days=i)

        kwh_lag1  = kwh_serie[-1] if len(kwh_serie) >= 1 else 0.0
        kwh_lag2  = kwh_serie[-2] if len(kwh_serie) >= 2 else kwh_lag1

        media_7d  = float(np.mean(kwh_serie[-7:]))  if len(kwh_serie) >= 7  else float(np.mean(kwh_serie or [0]))
        media_24h = float(np.mean(kwh_serie[-24:])) if len(kwh_serie) >= 24 else media_7d

        fila = {
            'potencia':      potencia_prom,
            'hora':          12,
            'dia_semana':    fecha_pred.weekday(),
            'mes':           fecha_pred.month,
            'kwh_lag_1':     kwh_lag1,
            'kwh_lag_2':     kwh_lag2,
            'kwh_media_7d':  media_7d,
            'kwh_media_24h': media_24h,
        }

        X = np.array([[fila[f] for f in features]])
        X_sc = scaler.transform(X)

        kwh_pred   = max(0.0, float(modelo.predict(X_sc)[0]))
        costo_pred = round(kwh_pred * tarifa, 0)

        resultados.append({
            'fecha': fecha_pred.strftime('%Y-%m-%d'),
            'kwh':   round(kwh_pred, 4),
            'costo': costo_pred,
        })

        # Retroalimentar el historial con la predicción
        kwh_serie.append(kwh_pred)

    return resultados


# ── Helpers para obtener datos desde la BD ──────────────────────────

def _obtener_kwh_historico_bd() -> list:
    """Lee las últimas mediciones y devuelve kWh diario histórico."""
    try:
        from mediciones.models import Medicion   # ajusta el import si tu app tiene otro nombre

        qs = (
            Medicion.objects
            .order_by('-fecha')
            .values('potencia', 'fecha')[:500]
        )
        if not qs:
            return [0.0]

        df = pd.DataFrame(list(qs))
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha').reset_index(drop=True)

        df['intervalo_h'] = df['fecha'].diff().dt.total_seconds() / 3600
        df['intervalo_h'] = df['intervalo_h'].fillna(1.0).clip(0, 24)
        df['kwh']         = df['potencia'] * df['intervalo_h'] / 1000

        df['dia'] = df['fecha'].dt.date
        kwh_diario = df.groupby('dia')['kwh'].sum().tolist()
        return kwh_diario if kwh_diario else [0.0]

    except Exception:
        return [0.0]


def _obtener_potencia_prom_bd() -> float:
    """Devuelve la potencia promedio de las últimas mediciones."""
    try:
        from mediciones.models import Medicion
        from django.db.models import Avg

        resultado = Medicion.objects.order_by('-fecha')[:168].aggregate(Avg('potencia'))
        return float(resultado.get('potencia__avg') or 1000.0)
    except Exception:
        return 1000.0