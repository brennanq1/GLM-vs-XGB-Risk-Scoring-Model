DROP TABLE IF EXISTS policies;
DROP TABLE IF EXISTS claims;

CREATE TABLE policies (
    IDpol INTEGER PRIMARY KEY,
    ClaimNb INTEGER UNIQUE NOT NULL,
    exposure VARCHAR(50),
    Area TEXT NOT NULL,
    VehPower INTEGER NOT NULL,
    VehAge INTEGER NOT NULL,
    DrivAge INTEGER NOT NULL,
    BonusMalus INTEGER NOT NULL,
    VehBrand VARCHAR(3) NOT NULL,
    VehGas TEXT NOT NULL,
    Density INTEGER NOT NULL,
    Region VARCHAR(3)
);

CREATE TABLE password_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    password_hash TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);