import os
import pandas as pd
import pytest
from pymongo import MongoClient
from pymongo.errors import OperationFailure


MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
DB_NAME = "datasolutech_medical"

ANALYST_USER = os.getenv("ANALYST_USER", "analyst_user")
ANALYST_PASS = os.getenv("ANALYST_PASSWORD", "analyst_password_123")

@pytest.fixture
def db_analyst():
    """Connexion avec le profil Analyste (lecture seule)."""
    uri = f"mongodb://{ANALYST_USER}:{ANALYST_PASS}@{MONGO_HOST}:{MONGO_PORT}/{DB_NAME}"
    client = MongoClient(uri)
    yield client[DB_NAME]
    client.close()

def test_volumetrie_donnees(db_analyst):
    """Vérifie que le nombre de documents correspond au CSV nettoyé."""
    df = pd.read_csv(os.path.join("data", "healthcare_dataset.csv")).drop_duplicates()
    nb_mongo = db_analyst["admissions"].count_documents({})
    assert nb_mongo == len(df), f"Attendu {len(df)} documents, trouvé {nb_mongo}"

def test_schema_et_types(db_analyst):
    """Vérifie la structure imbriquée et les types des variables sur un document."""
    doc = db_analyst["admissions"].find_one()
    assert doc is not None, "La collection est vide !"
    
    # Vérification des sections principales
    for section in ["patient", "medical_details", "hospital_stay", "billing"]:
        assert section in doc, f"Section manquante : {section}"
    
    # Vérification des types critiques
    assert isinstance(doc["patient"]["age"], int)
    assert isinstance(doc["billing"]["amount"], float)
    assert isinstance(doc["hospital_stay"]["room_number"], int)

def test_securite_lecture_seule(db_analyst):
    """Vérifie qu'un analyste ne peut pas modifier ou supprimer des données."""
    with pytest.raises(OperationFailure):
        db_analyst["admissions"].delete_one({})
