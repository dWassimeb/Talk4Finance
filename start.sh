#!/bin/bash
# Démarrer le backend en arrière-plan
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1

# Démarrer le frontend en premier plan
uvicorn npm start