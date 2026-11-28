import os
import pandas as pd
from pymongo import MongoClient

# Récupération des paramètres de connexion (compatibles local et Docker)
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")
DB_NAME = "datasolutech_medical"

def extract_and_clean_data(csv_path: str) -> pd.DataFrame:
    """Lit le fichier CSV source, nettoie les champs et supprime les doublons."""
    print("1. Lecture du fichier CSV...")
    df = pd.read_csv(csv_path)
    print(f"   -> {len(df)} lignes lues dans le fichier source.")

    print("2. Nettoyage et standardisation des données...")
    df["Name"] = df["Name"].str.strip().str.title()
    df["Date of Admission"] = pd.to_datetime(df["Date of Admission"])
    df["Discharge Date"] = pd.to_datetime(df["Discharge Date"])

    nb_avant = len(df)
    df = df.drop_duplicates()
    print(f"   -> {nb_avant - len(df)} doublons supprimés ({len(df)} lignes uniques conservées).")
    return df

def transform_to_documents(df: pd.DataFrame) -> list[dict]:
    """Transforme le DataFrame en liste de documents JSON imbriqués pour MongoDB."""
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
    return documents

def load_to_mongodb(documents: list[dict]) -> None:
    """Insère les documents dans MongoDB et crée les index de recherche."""
    print("4. Connexion à MongoDB et insertion des données...")
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}"
    client = MongoClient(uri)
    db = client[DB_NAME]
    collection = db["admissions"]

    collection.delete_many({})
    collection.insert_many(documents)

    collection.create_index("patient.name")
    collection.create_index("medical_details.condition")
    collection.create_index("hospital_stay.date_of_admission")

    print(f"Migration terminée avec succès : {collection.count_documents({})} documents insérés !")
    client.close()

def run_migration() -> None:
    """Orchestre le pipeline complet ETL (Extract, Transform, Load)."""
    csv_path = os.path.join("data", "healthcare_dataset.csv")
    df_clean = extract_and_clean_data(csv_path)
    documents = transform_to_documents(df_clean)
    load_to_mongodb(documents)

if __name__ == "__main__":
    run_migration()