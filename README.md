# 🏥 Migration de Données Médicales vers MongoDB & Déploiement Docker (DataSoluTech)

## 📋 Contexte du projet
Ce projet a été réalisé dans le cadre d'une mission de Data Engineering pour **DataSoluTech**. L'objectif est de migrer un jeu de données médicales de patients (`healthcare_dataset.csv`, 55 500 enregistrements) vers une base de données NoSQL **MongoDB** scalable horizontalement, le tout entièrement conteneurisé avec **Docker** et validé par des tests automatisés.

---

## 🏗️ Architecture du projet
```text
datasolutech-migration/
├── data/
│   └── healthcare_dataset.csv      # Dataset source (Kaggle)
├── mongo-init/
│   └── init-users.js               # Script d'initialisation des rôles et utilisateurs
├── src/
│   ├── migrate.py                  # Script ETL (Nettoyage, transformation, insertion, indexation)
│   └── test_migration.py           # Suite de tests d'intégrité et de sécurité (Pytest)
├── Dockerfile                      # Image Python pour l'exécution de l'ETL et des tests
├── docker-compose.yml              # Orchestration des services MongoDB et Migration
├── requirements.txt                # Dépendances Python
└── README.md                       # Documentation du projet
```

---

## 🗄️ Schéma de la base de données (`datasolutech_medical`)
Plutôt que de conserver une structure tabulaire à plat (15 colonnes), les données ont été modélisées sous forme de **documents JSON imbriqués** dans la collection `admissions` afin d'optimiser les performances de lecture et regrouper les informations logiques :

```json
{
  "_id": "ObjectId('...')",
  "patient": {
    "name": "Bobby Jackson",
    "age": 30,
    "gender": "Male",
    "blood_type": "B-"
  },
  "medical_details": {
    "condition": "Cancer",
    "medication": "Paracetamol",
    "test_results": "Normal"
  },
  "hospital_stay": {
    "hospital": "Sons and Miller",
    "doctor": "Matthew Smith",
    "admission_type": "Urgent",
    "room_number": 328,
    "date_of_admission": "ISODate('2024-01-31T00:00:00Z')",
    "discharge_date": "ISODate('2024-02-02T00:00:00Z')"
  },
  "billing": {
    "insurance_provider": "Blue Cross",
    "amount": 18856.28
  }
}
```
* **Nettoyage effectué :** Normalisation de la casse des noms (`Title Case`), typage strict des dates (`ISODate`) et des montants (`Float`), et suppression des **534 doublons exacts** (54 966 documents uniques conservés).
* **Indexation :** Création d'index sur `patient.name`, `medical_details.condition` et `hospital_stay.date_of_admission` pour accélérer les requêtes analytiques.

---

## 🔐 Authentification et gestion des rôles (RBAC)
Conformément aux bonnes pratiques de sécurité et au **principe du moindre privilège** appliqué aux données médicales, l'accès à MongoDB est protégé par authentification avec trois profils distincts configurés via `mongo-init/init-users.js` :

| Utilisateur | Rôle MongoDB | Base ciblée | Permissions et usage |
| :--- | :--- | :--- | :--- |
| **`admin`** | `root` | `admin` | **Administration complète** du serveur, gestion des utilisateurs et maintenance. |
| **`etl_user`** | `readWrite` | `datasolutech_medical` | **Lecture et écriture.** Utilisé exclusivement par le script automatisé `migrate.py`. |
| **`analyst_user`** | `read` | `datasolutech_medical` | **Lecture seule.** Destiné aux Data Analysts et au personnel médical pour l'exploration sans risque d'altération. |

---

## 🚀 Installation et exécution

### Prérequis
* [Docker Desktop](https://docker.com) installé et démarré.

### Lancer la migration et les tests en une commande
1. Cloner le dépôt et se placer à la racine du projet :
   ```bash
   git clone <URL_DE_TON_REPO_GITHUB>
   cd datasolutech-migration
   ```
2. Démarrer l'infrastructure en arrière-plan :
   ```bash
   docker compose up -d --build
   ```
3. Vérifier les logs de migration et le résultat des tests automatisés (`pytest`) :
   ```bash
   docker logs datasolutech_migration
   ```
