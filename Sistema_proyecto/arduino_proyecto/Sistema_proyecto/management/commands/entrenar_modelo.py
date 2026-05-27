import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from django.core.management.base import BaseCommand
from django.conf import settings
from mediciones.models import Medicion


ML_DIR = os.path.join(settings.BASE_DIR, 'ml_models')

# 💲 Tarifa eléctrica en tu moneda (ej: pesos/kWh). Ajusta según tu país/proveedor.
TARIFA_KWH = 150


class Command(BaseCommand):
    help = 'Entrena modelo de predicción energética y de costos futuros.'

    def handle(self, *args, **kwargs):
        os.makedirs(ML_DIR, exist_ok=True)

        df = self._cargar_datos_reales()

        if df is None or len(df) < 100:
            self.stdout.write(self.style.WARNING(
                f'Datos reales insuficientes ({len(df) if df is not None else 0}). '
                f'Usando datos sintéticos.'
            ))
            df = self._generar_datos_sinteticos()
        else:
            self.stdout.write(self.style.SUCCESS(f'Usando {len(df)} registros reales.'))

        # ✅ Crear features de lag (historial temporal) para predecir el futuro
        df = self._crear_features_lag(df)

        features = [
            'potencia',       # NO incluir voltaje+corriente+potencia juntos (redundancia)
            'hora',
            'dia_semana',
            'mes',
            'kwh_lag_1',      # consumo en el periodo anterior
            'kwh_lag_2',      # consumo hace 2 periodos
            'kwh_media_7d',   # promedio últimos 7 días
            'kwh_media_24h',  # promedio últimas 24 horas
        ]

        X = df[features]
        y_kwh = df['kwh']

        # ✅ Split TEMPORAL (no aleatorio) para respetar el orden cronológico
        split = int(len(df) * 0.8)
        X_train = X.iloc[:split]
        X_test  = X.iloc[split:]
        y_train = y_kwh.iloc[:split]
        y_test  = y_kwh.iloc[split:]

        # Escalado
        scaler = StandardScaler()
        X_train_sc = scaler.fit_transform(X_train)
        X_test_sc  = scaler.transform(X_test)

        # Entrenamiento
        self.stdout.write('Entrenando modelo RandomForest...')
        modelo = RandomForestRegressor(
            n_estimators=200,
            max_depth=12,
            min_samples_leaf=5,   # evita sobreajuste
            random_state=42,
            n_jobs=-1
        )
        modelo.fit(X_train_sc, y_train)

        # Evaluación
        y_pred_kwh = modelo.predict(X_test_sc)
        mae = mean_absolute_error(y_test, y_pred_kwh)
        r2  = r2_score(y_test, y_pred_kwh)

        # ✅ Calcular costo predicho
        y_pred_costo = y_pred_kwh * TARIFA_KWH
        y_real_costo = y_test * TARIFA_KWH
        mae_costo = mean_absolute_error(y_real_costo, y_pred_costo)

        # Guardar modelo, scaler y metadata
        joblib.dump(modelo, os.path.join(ML_DIR, 'modelo_energia.pkl'))
        joblib.dump(scaler, os.path.join(ML_DIR, 'scaler.pkl'))
        joblib.dump(features, os.path.join(ML_DIR, 'features.pkl'))
        joblib.dump({'tarifa': TARIFA_KWH}, os.path.join(ML_DIR, 'config.pkl'))

        self.stdout.write(self.style.SUCCESS('✅ Modelo guardado en ml_models/'))
        self.stdout.write(self.style.SUCCESS(
            f'📊 MAE kWh: {mae:.4f} | R²: {r2:.4f} | MAE Costo: ${mae_costo:.2f}'
        ))

        # Mostrar importancia de features
        importancias = pd.Series(modelo.feature_importances_, index=features)
        self.stdout.write('\n📌 Importancia de variables:')
        for feat, val in importancias.sort_values(ascending=False).items():
            self.stdout.write(f'   {feat}: {val:.4f}')

    # ------------------------------------------------------------------
    # 🔹 CARGA DE DATOS REALES
    # ------------------------------------------------------------------
    def _cargar_datos_reales(self):
        try:
            qs = Medicion.objects.values('voltaje', 'corriente', 'potencia', 'fecha').order_by('fecha')

            if not qs.exists():
                return None

            df = pd.DataFrame(list(qs))
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha').reset_index(drop=True)

            # ✅ Calcular kWh con el intervalo REAL entre mediciones
            df['intervalo_horas'] = df['fecha'].diff().dt.total_seconds() / 3600
            df['intervalo_horas'] = df['intervalo_horas'].fillna(1.0)  # primera medición: asumir 1h
            df['intervalo_horas'] = df['intervalo_horas'].clip(0, 24)   # limitar a 24h máximo

            df['kwh'] = df['potencia'] * df['intervalo_horas'] / 1000

            # Features temporales
            df['hora']       = df['fecha'].dt.hour
            df['dia_semana'] = df['fecha'].dt.weekday
            df['mes']        = df['fecha'].dt.month

            df = df.dropna(subset=['voltaje', 'corriente', 'potencia', 'kwh'])

            # ✅ Eliminar outliers extremos (potencia negativa o irreal)
            df = df[df['potencia'] > 0]
            df = df[df['kwh'] > 0]

            return df

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error cargando datos reales: {e}'))
            return None

    # ------------------------------------------------------------------
    # 🔹 DATOS SINTÉTICOS (más realistas)
    # ------------------------------------------------------------------
    def _generar_datos_sinteticos(self):
        self.stdout.write('Generando datos sintéticos...')

        np.random.seed(42)
        n = 4000  # más datos para mejor representación

        # Fechas continuas cada 1 hora (esencial para lag features)
        fechas = pd.date_range(start='2024-01-01', periods=n, freq='h')

        hora       = fechas.hour
        dia_semana = fechas.weekday
        mes        = fechas.month

        voltaje   = np.random.normal(220, 5, n)
        corriente = np.random.uniform(0.5, 15, n)

        # Factor de potencia realista
        fp = np.random.uniform(0.85, 0.98, n)
        potencia = voltaje * corriente * fp

        # Consumo base con variación horaria y diaria realista
        base = potencia / 1000  # kW → kWh por hora
        variacion_hora  = np.where((hora >= 18) & (hora <= 22), 1.4, 1.0)  # pico nocturno
        variacion_dia   = np.where(dia_semana < 5, 1.2, 0.9)               # más consumo en semana
        variacion_mes   = 1 + 0.05 * np.sin((mes - 1) * np.pi / 6)        # variación estacional

        kwh = base * variacion_hora * variacion_dia * variacion_mes
        kwh += np.random.normal(0, 0.05 * kwh, n)  # ruido proporcional al valor
        kwh = np.clip(kwh, 0.01, 50)

        df = pd.DataFrame({
            'fecha':     fechas,
            'voltaje':   voltaje,
            'corriente': corriente,
            'potencia':  potencia,
            'hora':      hora,
            'dia_semana': dia_semana,
            'mes':       mes,
            'kwh':       kwh
        })

        return df

    # ------------------------------------------------------------------
    # 🔹 FEATURES DE LAG (historial para predecir el futuro)
    # ------------------------------------------------------------------
    def _crear_features_lag(self, df):
        df = df.copy().reset_index(drop=True)

        # Consumo en periodos anteriores
        df['kwh_lag_1'] = df['kwh'].shift(1)
        df['kwh_lag_2'] = df['kwh'].shift(2)

        # Promedio móvil: últimas 24 horas y últimos 7 días
        df['kwh_media_24h'] = df['kwh'].rolling(window=24,  min_periods=1).mean().shift(1)
        df['kwh_media_7d']  = df['kwh'].rolling(window=168, min_periods=1).mean().shift(1)

        # Eliminar filas donde los lags son NaN (primeras filas)
        df = df.dropna(subset=['kwh_lag_1', 'kwh_lag_2']).reset_index(drop=True)

        return df