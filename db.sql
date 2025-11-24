-- [1]: Create DB and use it
CREATE DATABASE IF NOT EXISTS horse_racing_db DEFAULT CHARACTER SET utf8mb4;
USE horse_racing_db;

-- [2]: Drop (clean start)
DROP TABLE IF EXISTS RaceResults;
DROP TABLE IF EXISTS Race;
DROP TABLE IF EXISTS Track;
DROP TABLE IF EXISTS Owns;
DROP TABLE IF EXISTS Trainer;
DROP TABLE IF EXISTS Horse;
DROP TABLE IF EXISTS Stable;
DROP TABLE IF EXISTS Owner;
DROP TABLE IF EXISTS old_info;

-- [3]: Creating Tables 
create table Stable(
    stableId varchar(15) not null,
    stableName varchar(30),
    location varchar(30),
    colors varchar(20),
    primary key (stableId)
);


create table Horse(
    horseId varchar(15) not null,
    horseName varchar(15) not null,
    age int,
    gender char,
    registration integer not null,
    stableId varchar(30) not null,
    foreign key(stableId) references Stable(stableId),
    primary key(horseId)
);

create table Owner(
    ownerId varchar(15) not null,
    lname varchar(15),
    fname varchar(15),
    primary key(ownerId)
);

create table Owns(
    ownerId varchar(15) not null,
    horseId varchar(15) not null,
    primary key(ownerId, horseId),
    foreign key(ownerId) references Owner(ownerId),
    foreign key(horseId) references Horse(horseId)
);

create table Trainer(
    trainerId varchar(15) not null,
    lname varchar(30),
    fname varchar(30),
    stableId varchar(30),
    primary key(trainerId),
    foreign key(stableId) references Stable(stableId)
);

create table Track(
    trackName varchar(30) not null,
    location varchar(30),
    length integer,
    primary key(trackName)
);

create table Race(
    raceId varchar(15) not null,
    raceName varchar(30),
    trackName varchar(30),
    raceDate date,
    raceTime time,
    primary key(raceId),
    foreign key (trackName) references Track(trackName)
);

create table RaceResults(
    raceId varchar(15) not null,
    horseId varchar(15) not null,
    results varchar(15),
    prize float(10,2),
    primary key (raceId, horseId),
    foreign key(raceId) references Race(raceId),
    foreign key(horseId) references Horse(horseId)
);

-- [4]:  Add data to tables 
insert into Stable values ('stable1', 'Zobair Farm', 'Riyadh', 'orange');
insert into Stable values ('stable2', 'Zayed Farm', 'Dubai', 'kiwi');
insert into Stable values ('stable3', 'Zahra Farm', 'Jeddah', 'cinnamon');
insert into Stable values ('stable4', 'Sunny Stables', 'Jubail', 'lemon');
insert into Stable values ('stable5', 'Ajman Stables', 'Ajman', 'lemon');
insert into Stable values ('stable6', 'Dubai Stables', 'Dubai', 'bright blue');

insert into Horse values ('horse1', 'Warrior', 2, 'C', '11111', 'stable1');
insert into Horse values ('horse2', 'Conquerer', 2, 'F', '22222', 'stable6');
insert into Horse values ('horse3', 'Dove of Peace', 3, 'C', '33333','stable1');
insert into Horse values ('horse4', 'Ever Faster', 3, 'F', '44444','stable3');
insert into Horse values ('horse5', 'Slow Winner', 2, 'C', '55555','stable3');
insert into Horse values ('horse6', 'Windrunner', 2, 'F', '66666','stable2');
insert into Horse values ('horse7', 'Catapult', 4, 'M', '77777', 'stable6');
insert into Horse values ('horse8', 'Flying Force', 2, 'C', '88888','stable4');
insert into Horse values ('horse9', 'Laggard', 2, 'F', '99999', 'stable4');
insert into Horse values ('horse10', 'Formula One', 6, 'G', '10101','stable2');
insert into Horse values ('horse11', 'Frisky Frolic', 3, 'C', '11011','stable4');
insert into Horse values ('horse12', 'Fantastic', 3, 'F', '12121','stable2');
insert into Horse values ('horse13', 'Midnight', 2, 'C', '13131', 'stable3');
insert into Horse values ('horse14', 'Running Wild', 4, 'S', '14141','stable2');
insert into Horse values ('horse15', 'FastOffMyFeet', 3, 'C', '15151','stable1');
insert into Horse values ('horse16', 'Slow Poke', 2, 'C', '16161','stable3');
insert into Horse values ('horse17', 'Slinger', 3, 'F', '17171', 'stable2');
insert into Horse values ('horse18', 'Sublime', 5, 'M', '18181', 'stable6');
insert into Horse values ('horse19', 'Front Runner', 4, 'G', '19191','stable4');
insert into Horse values ('horse20', 'Night', 3, 'C', '20200', 'stable1');
insert into Horse values ('horse21', 'Negative', 3, 'F', '21210', 'stable3');
insert into Horse values ('horse22', 'Lightening', 2, 'C', '22220','stable6');
insert into Horse values ('horse23', 'Lazy Loser', 4, 'G', '23230','stable1');
insert into Horse values ('horse24', 'Leaping Lizard', 2, 'C', '24240','stable1');
insert into Horse values ('horse25', 'Beautiful Brown ', 3, 'F', '25250','stable6');
insert into Horse values ('horse26', 'Sick Winner', 5, 'M', '26260','stable2');

insert into Owner values('owner1', 'Saeed', 'Ahmed');
insert into Owner values('owner2', 'Mohammed', 'Khalid');
insert into Owner values('owner3', 'Mohammed', 'Faisal');
insert into Owner values('owner4', 'Fahd', 'Abdul Rahman');
insert into Owner values('owner5', 'Nasr', '');
insert into Owner values('owner6', 'Mohammed', 'Sheikh');
insert into Owner values('owner7', 'Abed', 'Ahmed');
insert into Owner values('owner8', 'Mashour', '');
insert into Owner values('owner9', 'Said', 'Sheikh');
insert into Owner values('owner10', 'Faisal', 'Khan');
insert into Owner values('owner11', 'Jabr', 'Mohammed');
insert into Owner values('owner12', 'Faleh', 'Mahmood');
insert into Owner values('owner13', 'Yahya', 'Mohammed');
insert into Owner values('owner14', 'Sulaiman', '');
insert into Owner values('owner15', 'Saeed', 'Ali');
insert into Owner values('owner16', 'Ahmed', 'Faisal');
insert into Owner values('owner17', 'Saud', 'Mohammed');
insert into Owner values('owner18', 'Nazir', 'Mohammed');
insert into Owner values('owner19', 'Saleh', 'Fahd');
insert into Owner values('owner20', 'Mohammed', 'Naeem');

insert into Owns values('owner14', 'horse1');
insert into Owns values('owner3', 'horse2');
insert into Owns values('owner2', 'horse3');
insert into Owns values('owner2', 'horse4');
insert into Owns values('owner1', 'horse5');
insert into Owns values('owner12', 'horse5');
insert into Owns values('owner14', 'horse5');
insert into Owns values('owner1', 'horse6');
insert into Owns values('owner5', 'horse6');
insert into Owns values('owner20', 'horse7');
insert into Owns values('owner19', 'horse8');
insert into Owns values('owner2', 'horse9');
insert into Owns values('owner18', 'horse10');
insert into Owns values('owner3', 'horse10');
insert into Owns values('owner4', 'horse11');
insert into Owns values('owner16', 'horse12');
insert into Owns values('owner17', 'horse13');
insert into Owns values('owner15', 'horse14');
insert into Owns values('owner15', 'horse15');
insert into Owns values('owner20', 'horse16');
insert into Owns values('owner4', 'horse17');
insert into Owns values('owner6', 'horse19');
insert into Owns values('owner12', 'horse20');
insert into Owns values('owner7', 'horse21');
insert into Owns values('owner7', 'horse22');
insert into Owns values('owner10', 'horse23');
insert into Owns values('owner12', 'horse24');
insert into Owns values('owner13', 'horse25');
insert into Owns values('owner2', 'horse26');
insert into Owns values('owner9', 'horse23');
insert into Owns values('owner8', 'horse18');

insert into Trainer values('trainer1', 'Mohammed', 'Fahd', 'stable2');
insert into Trainer values('trainer2', 'Saleh', 'Saeed', 'stable1');
insert into Trainer values('trainer3', 'Ali', 'Raad', 'stable4');
insert into Trainer values('trainer4', 'Sayed', 'Wasim', 'stable3');
insert into Trainer values('trainer5', 'Ahmed', 'Ali', 'stable3');
insert into Trainer values('trainer6', 'Faisal', 'Salah', 'stable5');
insert into Trainer values('trainer7', 'Hamid', 'Ahmed', 'stable6');
insert into Trainer values('trainer8', 'Khalid', 'Ahmed', 'stable6');

insert into Track values('Doha', 'QT', 20);
insert into Track values('Jubail', 'SA', 15);
insert into Track values('Yanbu', 'SA', 18);
insert into Track values('Dubai', 'UE', 17);
insert into Track values('Jeddah', 'SA', 19);
insert into Track values('Bahrain', 'BH', 18);
insert into Track values('Sharjah', 'UE', 20);
insert into Track values('Riyadh', 'SA', 22);
insert into Track values('Dhahran', 'SA', 20);

insert into Race values('race1', 'Kings Cup', 'Riyadh', '2007-05-03','14:00');
insert into Race values('race2', '2-year-old fillies', 'Doha', '2007-05-03','13:00');
insert into Race values('race3', '2-year-old colts', 'Doha', '2007-05-03','13:30');
insert into Race values('race4', 'Handicap', 'Doha', '2007-05-03','12:00');
insert into Race values('race5', 'Claiming Stake', 'Sharjah', '2007-05-03','12:30');
insert into Race values('race6', '3-year-old fillies', 'Jubail', '2007-06-02','12:30');
insert into Race values('race7', 'Handicap', 'Jubail', '2007-06-02','9:30');
insert into Race values('race8', '2-year-old colts', 'Riyadh', '2007-06-02','10:30');
insert into Race values('race9', '2-year-old fillies', 'Jubail', '2007-06-02','11:30');
insert into Race values('race10', 'Claiming Stake', 'Sharjah', '2007-06-02','12:30');
insert into Race values('race11', '3-year-old fillies', 'Dubai', '2007-04-02','10:30');
insert into Race values('race12', 'Handicap', 'Yanbu', '2007-05-03','11:30');
insert into Race values('race13', '3-year-old fillies', 'Yanbu', '2007-05-03','11:00');
insert into Race values('race14', 'Handicap', 'Dhahran', '2007-05-10','10:00');
insert into Race values('race15', '3-year-old colts', 'Dubai', '2007-05-12','15:00');
insert into Race values('race16', 'Claiming Stake', 'Yanbu', '2007-05-20','14:30');
insert into Race values('race17', 'Handicap', 'Doha', '2007-05-20','13:00');
insert into Race values('race18', '3-year-old fillies', 'Sharjah', '2007-05-21','8:00');
insert into Race values('race19', '2-year-old colts', 'Dhahran', '2007-05-25','11:00');
insert into Race values('race20', 'Claiming Stake', 'Jeddah', '2007-05-25','8:30');
insert into Race values('race21', '3-year-old colts', 'Riyadh', '2007-03-19','14:30');
insert into Race values('race22', 'Handicap', 'Dhahran', '2007-03-27','15:00');
insert into Race values('race23', '3-year-old fillies', 'Jeddah', '2007-03-28','9:30');
insert into Race values('race24', '3-year-old colts', 'Jubail', '2007-03-28','13:30');
insert into Race values('race25', 'Claiming Stake', 'Jeddah', '2007-03-29','10:00');
insert into Race values('race26', '3-year-old colts', 'Yanbu', '2007-03-30','12:30');
insert into Race values('race27', 'Handicap', 'Dubai', '2007-04-03','14:00');
insert into Race values('race28', '2-year-old fillies', 'Jeddah', '2007-04-04','8:30');
insert into Race values('race29', '3-year-old colts', 'Bahrain', '2007-04-05','8:00');
insert into Race values('race30', 'Claiming Stake', 'Dhahran', '2007-04-08','9:30');
insert into Race values('race31', 'Handicap', 'Dhahran', '2007-04-08','9:00');
insert into Race values('race32', '2-year-old colts', 'Jubail', '2007-04-09','11:00');
insert into Race values('race33', 'Claiming Stake', 'Bahrain', '2007-04-10','13:00');
insert into Race values('race34', '3-year-old colts', 'Dubai', '2007-05-12','12:00');
insert into Race values('race35', 'Handicap', 'Dubai', '2007-04-13','10:30');
insert into Race values('race36', '3-year-old colts', 'Jeddah', '2007-05-03','14:30');

insert into RaceResults values('race1', 'horse3', 'first', 500000);
insert into RaceResults values('race1', 'horse11', 'second', 200000);
insert into RaceResults values('race1', 'horse15', 'third', 500000);
insert into RaceResults values('race2', 'horse6', 'first', 100000);
insert into RaceResults values('race2', 'horse2', 'second', 50000);
insert into RaceResults values('race2', 'horse20', 'third', 20000);
insert into RaceResults values('race3', 'horse22', 'first', 70000);
insert into RaceResults values('race3', 'horse5', 'second', 50000);
insert into RaceResults values('race3', 'horse1', 'third', 20000);
insert into RaceResults values('race4', 'horse19', 'first', 50000);
insert into RaceResults values('race4', 'horse18', 'no show', 0);
insert into RaceResults values('race4', 'horse14', 'no show', 0);
insert into RaceResults values('race6', 'horse25', 'first', 5000);
insert into RaceResults values('race7', 'horse7', 'second', 2000);
insert into RaceResults values('race9', 'horse11', 'last', 0);
insert into RaceResults values('race10', 'horse18', 'fourth', 500);
insert into RaceResults values('race11', 'horse12', 'first', 50000);
insert into RaceResults values('race11', 'horse17', 'second',25000);
insert into RaceResults values('race11', 'horse21', 'fourth', 10000);
insert into RaceResults values('race12', 'horse14', 'first', 6000);
insert into RaceResults values('race12', 'horse18', 'second', 5000);
insert into RaceResults values('race13', 'horse25', 'first', 100000);
insert into RaceResults values('race13', 'horse4', 'second', 50000);
insert into RaceResults values('race13', 'horse12', 'third', 30000);
insert into RaceResults values('race14', 'horse23', 'first', 25000);
insert into RaceResults values('race14', 'horse26', 'second', 20000);
insert into RaceResults values('race15', 'horse11', 'second', 10000);
insert into RaceResults values('race15', 'horse24', 'third', 8000);
insert into RaceResults values('race16', 'horse10', 'second', 5000);
insert into RaceResults values('race16', 'horse14', 'third', 4000);
insert into RaceResults values('race17', 'horse7', 'first', 15000);
insert into RaceResults values('race17', 'horse10', 'second',1100);
insert into RaceResults values('race18', 'horse6', 'first', 70000);
insert into RaceResults values('race19', 'horse22', 'first', 1000000);
insert into RaceResults values('race19', 'horse1', 'second', 80000);
insert into RaceResults values('race19', 'horse8', 'third', 60000);
insert into RaceResults values('race20', 'horse23', 'first', 1500);
insert into RaceResults values('race20', 'horse14', 'second', 1000);
insert into RaceResults values('race20', 'horse26', 'third', 800);
insert into RaceResults values('race20', 'horse10', 'fourth', 500);
insert into RaceResults values('race21', 'horse24', 'first', 70000);
insert into RaceResults values('race21', 'horse15', 'second', 55000);
insert into RaceResults values('race21', 'horse3', 'third', 40000);
insert into RaceResults values('race22', 'horse18', 'first', 10000);
insert into RaceResults values('race22', 'horse19', 'second', 8000);
insert into RaceResults values('race23', 'horse25', 'first', 150000 );
insert into RaceResults values('race24', 'horse7', 'first', 10000);
insert into RaceResults values('race25', 'horse10', 'second', 8000);
insert into RaceResults values('race25', 'horse20', 'fourth', 2000);
insert into RaceResults values('race26', 'horse24', 'first', 8000);
insert into RaceResults values('race26', 'horse20', 'fourth', 2000);
insert into RaceResults values('race27', 'horse18', 'first', 70000);
insert into RaceResults values('race27', 'horse23', 'third', 40000);
insert into RaceResults values('race28', 'horse25', 'first', 90000);
insert into RaceResults values('race29', 'horse15', 'first', 80000);
insert into RaceResults values('race29', 'horse3', 'second', 65000);
insert into RaceResults values('race29', 'horse24', 'third', 50000);
insert into RaceResults values('race30', 'horse14', 'second', 1500);
insert into RaceResults values('race30', 'horse10', 'fourth', 500);
insert into RaceResults values('race31', 'horse7', 'first', 90000);
insert into RaceResults values('race31', 'horse26', 'second', 70000);
insert into RaceResults values('race31', 'horse23', 'third', 50000);
insert into RaceResults values('race31', 'horse10', 'fourth', 30000);
insert into RaceResults values('race32', 'horse22', 'first', 150000);
insert into RaceResults values('race32', 'horse13', 'second', 125000);
insert into RaceResults values('race32', 'horse16', 'third', 100000);
insert into RaceResults values('race33', 'horse23', 'second', 1700);
insert into RaceResults values('race33', 'horse26', 'third', 1200);
insert into RaceResults values('race34', 'horse11', 'first', 50000);
insert into RaceResults values('race34', 'horse15', 'second', 30000);
insert into RaceResults values('race35', 'horse7', 'first', 45000);
insert into RaceResults values('race35', 'horse19', 'second', 25000);
insert into RaceResults values('race36', 'horse11', 'first', 100000);
insert into RaceResults values('race36', 'horse15', 'second', 80000);
insert into RaceResults values('race36', 'horse20', 'third', 50000);

