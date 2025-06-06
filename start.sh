#!/bin/bash

set -e  # Arrête le script à la première erreur
set -x  # Affiche chaque commande avant exécution

echo "Début du script de démarrage"
echo "Répertoire courant: $(pwd)"
echo "Contenu du répertoire:"
ls -la

echo "🔧 Vérification des dépendances..."
which npm || echo " npm non trouvé"
which uvicorn || echo " uvi non trouvé"

cd /app/backend
# Démarrer le backend en arrière-plan
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 1 &

#npm run build &
# Démarrer le frontend en premier plan
cd /app/frontend

npm start