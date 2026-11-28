db = db.getSiblingDB('datasolutech_medical');

// 1. Utilisateur pour le script de migration (Lecture + Écriture)
db.createUser({
  user: process.env.ETL_USER,
  pwd: process.env.ETL_PASSWORD,
  roles: [{ role: 'readWrite', db: 'datasolutech_medical' }]
});

// 2. Utilisateur pour les analystes / médecins (Lecture seule)
db.createUser({
  user: process.env.ANALYST_USER,
  pwd: process.env.ANALYST_PASSWORD,
  roles: [{ role: 'read', db: 'datasolutech_medical' }]
});