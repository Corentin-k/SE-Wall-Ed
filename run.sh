#!/bin/bash
cd backend && python3 run.py &

cd frontend && npm run dev -- --host

# Fonction de nettoyage à l'arrêt du script
cleanup() {
    sudo killall python3
    exit 0
}


trap cleanup SIGINT SIGTERM

npm run dev -- --host


#cleanup

