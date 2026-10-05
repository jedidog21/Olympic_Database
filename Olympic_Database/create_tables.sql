DROP TABLE IF EXISTS Events;
DROP TABLE IF EXISTS Athletes;
DROP TABLE IF EXISTS Regions;

CREATE TABLE Regions (
NOC VARCHAR(3) PRIMARY KEY NOT NULL,
Region TEXT NOT NULL,
Notes TEXT
);



CREATE TABLE Athletes(
ID INTEGER PRIMARY KEY NOT NULL,
Name TEXT NOT NULL,
Sex VARCHAR(1) NOT NULL CHECK(Sex IN ('F', 'M')),
Age INTEGER,
Height REAL,
Weight REAL
);

CREATE TABLE Events(
ID INTEGER NOT NULL,
Team TEXT NOT NULL,
NOC VARCHAR(3) NOT NULL,
Games TEXT NOT NULL,
Year INTEGER NOT NULL,
Season TEXT NOT NULL CHECK(Season IN ('Summer', 'Winter')),
City TEXT NOT NULL,
Sport TEXT NOT NULL,
Event TEXT NOT NULL,
Medal TEXT NOT NULL CHECK(Medal IN ('Gold', 'Silver', 'Bronze', 'NA')),

FOREIGN KEY (ID) REFERENCES Athletes(ID),
FOREIGN KEY (NOC) REFERENCES Regions(NOC)
);

\copy Regions(NOC, Region, Notes) FROM 'regions.csv' DELIMITER ',' CSV HEADER;

\copy Athletes(ID, Name, Sex, Age, Height, Weight) FROM 'athletes_info.csv' WITH (FORMAT CSV, HEADER, DELIMITER ';', NULL '');

\copy Events(ID, Team, NOC, Games, Year, Season, City, Sport, Event, Medal) FROM 'event_info.csv' WITH(FORMAT CSV, HEADER, DELIMITER ';');
