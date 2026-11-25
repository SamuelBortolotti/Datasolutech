import os
import pandas as pd
from pymongo import MongoClient

# Récupération des paramètres de connexion (compatibles local et Docker)
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER", "etl_user")
MONGO_PASS = os.getenv("MONGO_PASS", "etl_password_123")
DB_NAME = "datasolutech_medical"

def run_migration():
    print("1. Lecture du fichier CSV...")
    csv_path = os.path.join("data", "healthcare_dataset.csv")
    df = pd.read_csv(csv_path)
    print(f"   -> {len(df)} lignes lues dans le fichier source.")

    print("2. Nettoyage et standardisation des données...")
    # Normalisation des noms (ex: "bObBy jAcKsOn" -> "Bobby Jackson")
    df["Name"] = df["Name"].str.strip().str.title()
    
    # Conversion des dates au format datetime
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"])

    # Suppression des doublons exacts
    nb_avant = len(df)
    df = df.drop_duplicates()
    print(f"   -> {nb_avant - len(df)} doublons supprimés ({len(df)} lignes uniques conservées).")

    print("3. Transformation au format JSON imbriqué (Document MongoDB)...")
    documents = []
    for _, row in df.iterrows():
        doc = {
            "patient": {
                "name": row["Name"],
                "age": int(row["Age"]),
                "gender": row["Gender"],
                "blood_type": row["Blood Type"]
            },
            "medical_details": {
                "condition": row["Medical Condition"],
                "medication": row["Medication"],
                "test_results": row["Test Results"]
            },
            "hospital_stay": {
                "hospital": row["Hospital"],
                "doctor": row["Doctor"],
                "admission_type": row["Admission Type"],
                "room_number": int(row["Room Number"]),
                "date_of_admission": row["Date of Admission"],
                "discharge_date": row["Discharge Date"]
            },
            "billing": {
                "insurance_provider": row["Insurance Provider"],
                "amount": round(float(row["Billing Amount"]), 2)
            }
        }
        documents.append(doc)

    print("4. Connexion à MongoDB et insertion des données...")
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}"
    client = MongoClient(uri)
    db = client[DB_NAME]
    collection = db["admissions"]

    # Nettoyage préalable pour éviter les doublons si on relance le script
    collection.delete_many({})
    collection.insert_many(documents)

    # Création d'index pour accélérer les futures requêtes des médecins/analystes
    collection.create_index("patient.name")
    collection.create_index("medical_details.condition")
    collection.create_index("hospital_stay.date_of_admission")

    print(f"Migration terminée avec succès : {collection.count_documents({})} documents insérés !")
    client.close()

if __name__ == "__main__":
    run_migration()