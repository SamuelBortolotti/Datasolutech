db = db.getSiblingDB('datasolutech_medical');

// 1. Utilisateur pour le script de migration (Lecture + Écriture)
db.createUser({
  user: 'etl_user',
  pwd: 'etl_password_123',
  roles: [{ role: 'readWrite', db: 'datasolutech_medical' }]
});

// 2. Utilisateur pour les analystes / médecins (Lecture seule)
db.createUser({
  user: 'analyst_user',
  pwd: 'analyst_password_123',
  roles: [{ role: 'read', db: 'datasolutech_medical' }]
});