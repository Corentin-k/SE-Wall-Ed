# Robot Wall-Ed

## Contexte

Dans le cadre du MasterCamp « Systèmes embarqués » de troisième année à l’EFREI, nous avons conçu ("allons concevoir") **Wall-Ed**, un robot autonome capable de se déplacer, de percevoir son environnement et d’interagir avec celui-ci.

Pour cette première partie, l’objectif était de mettre en place les fondations logicielles et matérielles : communication client-serveur et commande des capteurs (moteurs, servos, LEDs).

## Architecture générale

Le projet se compose de deux modules principaux :

1. **Backend**

   - Langage : Python
   - Framework : Flask (exposition d’une API RESTful)
   - Fonctionnalités : contrôle des moteurs, des servomoteurs, des LEDs, acquisition vidéo, intégration des capteurs

2. **Frontend**

   - Langage : JavaScript
   - Framework : Vue.js
   - Rôle : interface web permettant le pilotage manuel du robot

## Structure du dépôt

```text
/.
├── backend/             # Serveur Flask et logique robotique
│   ├── api/             # Point d’entrée de l’application
│   │    ├── /routes/    # Définition des routes REST
│   ├── robot/           # Implémentation de la classe Robot et de ses composants
│   │    ├── /config.py  # Configuration des broches GPIO et canaux I2C
│   ├── sensors/         # Modules capteurs (distance, ligne, buzzer…)
│   └── requirements.txt
└── frontend/            # Application Vue.js
    ├── public/
    └── src/             # Composants, vues
```

## Installation

1. **Backend**

   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Frontend**

   ```bash
   cd ../frontend
   npm install
   ```

## Exécution

1. **Démarrage du serveur backend**

   ```bash
   cd backend
   source venv/bin/activate
   python run.py
   ```

   Serveur backend : `http://localhost:5000`.

2. **Lancement de l’interface frontend**

   ```bash
   cd frontend
   npm run dev -- --host
   ```

   Serveur web : `http://localhost:5173`.

3. Grâce au script `run.sh`, démarrage des deux serveurs en une seule commande :

   ```bash
   ./run.sh
   ```

## Phase 1 : 06/06/2024 – 11/06/2024

### Fonctionnalités implémentées

1. **Flux vidéo**

   - Captation continue via Picamera2
   - Affichage en temps réel dans l’interface web

2. **Commandes LED RGB**

   - Pilotage de deux LED rgb frontales (gauche/droite)
   - Choix de la couleur via code hexadécimal

3. **Contrôle de la tête (servomoteurs)**

   - Axe panoramique (gauche/droite)
   - Axe d’inclinaison (haut/bas)
   - Commande via l’interface web (I,J,K,L pour les mouvements)

4. **Capteurs embarqués**

   - Capteur de distance à ultrasons
   - Buzzer programmable
   - Motorisation DC avec gestion de l’accélération et de la décélération

---
