create table "Факультеты" (
  "ID_факультета" bigint primary key,
  "Название" varchar(40) not null,
  "ФИО_декана" varchar(40) not null,
  "Почта_факультета" varchar(40) not null
);
create table "Группы"(
  "Номер_группы" varchar(7) primary key,
  "Форма_обучения" varchar(30) not null,
  "Курс" integer not null,
  "ID_факультета" bigint not null,
  foreign key ("ID_факультета") references "Факультеты",
  constraint "проверка_курса"
    check ("Курс" <5)
);
create table "Студенты" (
  "Серия_и_номер_паспорта" bigint primary key,
    "ФИО" varchar(40) null,
    "Дата_рождения" date not null,
  "Почта" varchar(40) not null,
  "Группа" varchar(7) not null,
  foreign key ("Группа") references "Группы"
);
create table "Студенческие_билеты" (
  "Серия_и_номер_паспорта" bigint not null,
  "Номер_студенческого_билета" bigint not null,
  "Дата_получения" date not null,
  "До_какого_действителен" date not null,
  foreign key ("Серия_и_номер_паспорта") references "Студенты",
  constraint "Проверка_соответствия_дат"
    check ("Дата_получения"<"До_какого_действителен")
);
create table "Предприятия" (
  "ID_предприятия" integer primary key,
  "Название" varchar(40) unique,
  "Количество_доступных_мест" integer
);

create table "Трудовые_договоры" (
  "Номер_договора" bigint primary key,
  "Код_предприятия" integer not null,
  "Паспортные_данные_студента" bigint not null,
  "Дата_начала_практики" date not null,
  "Дата_окончания_договора" date not null,
  foreign key ("Паспортные_данные_студента") references "Студенты" ,
  foreign key ("Код_предприятия") references "Предприятия",
  constraint "Проверка_соответствия_дат"
    check ("Дата_начала_практики"<"Дата_окончания_договора")
);
CREATE ROLE readonly LOGIN NOSUPERUSER;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
create role "user" with
login
connection limit -1
password '123456';
create role "root" with
login
superuser
connection limit -1
password '123456';
GRANT readonly TO "user";