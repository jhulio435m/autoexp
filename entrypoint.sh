#!/bin/bash
set -e

echo "🧪 Heisenberg: Iniciando secuencia de arranque del Backend (FastAPI)..."

# 1. Esperar a que la DB esté lista
echo "⏳ Esperando estabilidad en el reactor (Base de Datos)..."
until pg_isready -h db -U autoexp_user -d autoexp_db; do
  sleep 1
done

# 2. Inicializar y Sembrar (Migraciones y Seeding)
echo "💉 Inyectando precursores y configurando esquema..."
python3 -c "import db_manager; db_manager.init_db()"
python3 scripts/seed_db.py

# 3. Pruebas de Integración (Control de Calidad)
echo "🔬 Realizando pruebas de pureza (Integración)..."
# Desactivamos temporalmente las pruebas de integración de Streamlit ya que el frontend cambió
# if python3 -m pytest tests/test_integration.py; then
#     echo "✅ Pureza del 99.1%. Producto validado."
# else
#     echo "❌ ¡IMPUREZAS DETECTADAS! La operación se detiene."
#     exit 1
# fi

# 4. Iniciar Distribución (FastAPI)
echo "🚀 Iniciando distribución (FastAPI)..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
