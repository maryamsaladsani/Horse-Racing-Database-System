# Horse Racing Database System

A comprehensive database management system for horse racing operations.

## 📋 Project Overview

This system manages horse racing data including horses, owners, trainers, stables, races, tracks, and race results. It provides a user-friendly interface with role-based access control for administrators and guests.

## 🎯 Features

### Admin Functions
- **Add New Race**: Record new races with complete race results
- **Delete Owner**: Remove an owner and all related information from the database
- **Move Horse**: Transfer a horse from one stable to another using horse ID
- **Approve Trainer**: Add new trainers to stables

### Guest Functions
- **Browse Horses by Owner**: View horse names, ages, and trainer information filtered by owner's last name
- **Browse Winning Trainers**: See trainers who have trained first-place winners with detailed race information
- **Trainer Winnings Report**: View trainers ranked by total prize money earned
- **Track Statistics**: List tracks with race counts and total horse participation

## 🗄️ Database Schema
### Tables
- **Stable**: Stable information (ID, name, location, colors)
- **Horse**: Horse details (ID, name, age, gender, registration, stable)
- **Owner**: Owner information (ID, first name, last name)
- **Owns**: Ownership relationships (many-to-many between owners and horses)
- **Trainer**: Trainer details (ID, name, stable affiliation)
- **Track**: Racing track information (name, location, length)
- **Race**: Race details (ID, name, track, date, time)
- **RaceResults**: Race outcomes (race ID, horse ID, result, prize money)

### Key Relationships
- Owners can own multiple horses across different stables
- Horses can have multiple owners
- Trainers work for a single stable
- Stables employ multiple trainers and house multiple horses
- Horses can participate in multiple races
- Trainers can also be owners

### Horse Gender Codes
- **F**: Filly (young female)
- **C**: Colt (young male)
- **M**: Mare (older female)
- **S**: Stallion (older male)
- **G**: Gelding (older neutered male)

## 🛠️ Technical Implementation
### Technologies
- **Database**: SQL (SQLite for development/testing)
- **Backend**: Python 
- **Frontend**: Streamlit
- **Database Interface**: sqlite3 module

### Stored Procedures & Triggers
1. **Stored Procedure**: `delete_owner_and_related_info` - Removes an owner and all associated data
2. **Trigger**: `backup_horse_on_delete` - Copies horse information to `old_info` table before deletion

## 📁 Project Structure

```
horse-racing-db/
├── app.py                          # Main Flask application
├── db.sql                          # DDL and DML statements
├── horse_racing_db.sqlite          # SQLite database file
├── horse-racing-db.code-workspace  # VS Code workspace configuration
└── README.md                       
```

## 🚀 Getting Started

### Prerequisites
- Python 3.7 or higher
- Streamlit
- SQLite3 (included with Python)


### Installation

1. Clone the repository or download the project files

2. Install required Python packages:
```bash
pip install streamlit
pip install pandas  # For data manipulation
```

3. Set up the database:
```bash
# The SQLite database file (horse_racing_db.sqlite) is included
# If you need to recreate it, run:
sqlite3 horse_racing_db.sqlite < db.sql
```

4. Run the application:
```bash
streamlit run app.py
```

5. The application will automatically open in your web browser at:
```
http://localhost:8501
```

## 👥 User Roles

### Admin Access
- Full database modification privileges
- Can add, delete, and modify records
- Manages race results and trainer approvals

### Guest Access
- Read-only access
- Browse and query data
- Generate reports

## 📊 Sample Data

The database comes pre-populated with:
- 6 stables (Zobair Farm, Zayed Farm, Zahra Farm, Sunny Stables, Ajman Stables, Dubai Stables)
- 26 horses with various ages and genders
- 20 owners
- 8 trainers
- 8 racing tracks across the Gulf region
- 36 races with complete results
- Multiple race results with prize money

## 🔍 Sample Queries

### Find horses owned by a specific person
```sql
SELECT h.horseName, h.age, t.fname, t.lname
FROM Horse h
JOIN Owns o ON h.horseId = o.horseId
JOIN Owner ow ON o.ownerId = ow.ownerId
JOIN Trainer t ON h.stableId = t.stableId
WHERE ow.lname = 'Mohammed';
```

### List winning trainers
```sql
SELECT DISTINCT t.fname, t.lname, h.horseName, r.raceName
FROM Trainer t
JOIN Stable s ON t.stableId = s.stableId
JOIN Horse h ON s.stableId = h.stableId
JOIN RaceResults rr ON h.horseId = rr.horseId
JOIN Race r ON rr.raceId = r.raceId
WHERE rr.results = 'first';
```

### Trainer winnings summary
```sql
SELECT t.fname, t.lname, SUM(rr.prize) as total_winnings
FROM Trainer t
JOIN Stable s ON t.stableId = s.stableId
JOIN Horse h ON s.stableId = h.stableId
JOIN RaceResults rr ON h.horseId = rr.horseId
GROUP BY t.trainerId
ORDER BY total_winnings DESC;
```



## 📖 Additional Notes

- The system uses procedural SQL for complex operations
- Triggers automatically backup data before deletion
- All monetary values are stored as float(10,2) for precision
- Dates and times are properly formatted for race scheduling

## 👥 Team Members

| Name              | GitHub                                                                  |
|-------------------|-------------------------------------------------------------------------|
|  Maryam Aladsani  | [maraymsaladsani](https://github.com/your-github-maraymsaladsani) | 
|  Somaia Khawaji   | [Somaiakha](https://github.com/Somaiakha)                              | 

Developed as part of ICS321 Project #1.

## 📄 License

This project is created for educational purposes as part of the ICS321 course curriculum.

---

**Project Documentation**: ICS321-Project_1.pdf  
**Database Schema**: db.sql  
**Application Code**: app.py
