DROP VIEW IF EXISTS risk_model_view;
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS policies;

CREATE TABLE policies (
    IDpol INTEGER PRIMARY KEY,
    ClaimNb INTEGER NOT NULL,
    Exposure REAL NOT NULL,
    Area TEXT NOT NULL,
    VehPower INTEGER NOT NULL,
    VehAge INTEGER NOT NULL,
    DrivAge INTEGER NOT NULL,
    BonusMalus INTEGER NOT NULL,
    VehBrand TEXT NOT NULL,
    VehGas TEXT NOT NULL,
    Density INTEGER NOT NULL,
    Region TEXT
);

CREATE TABLE claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    IDpol INTEGER NOT NULL,
    ClaimAmount REAL NOT NULL,
    FOREIGN KEY (IDpol) REFERENCES policies(IDpol)
);

CREATE VIEW risk_model_view AS
SELECT 
    p.*, 
    COALESCE(SUM(c.ClaimAmount), 0) AS TotalClaimAmount
FROM policies p
LEFT JOIN claims c ON p.IDpol = c.IDpol
GROUP BY p.IDpol;