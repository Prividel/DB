#include <QCoreApplication>
#include <QSqlDatabase>
#include <QSqlError>
#include <QSqlQuery>
#include <QDebug>
#include <QSqlRecord>
#include <QDate>
#include <iostream>

bool isNumeric(QString const& str){
    return !str.isEmpty() && str.toDouble() != 0;
}
bool isString(QString const& str){
    return !str.isEmpty() && !str.contains(QRegExp("[0-9]"));
}
bool isDate(QString const& str, QString const& format = "dd-MM-yyyy"){
    QDate date = QDate::fromString(str, format);
    return date.isValid();
}
void correctApostrof(std::string &query){
    size_t pos;
    while ((pos = query.find('\'')) != std::string::npos) {
        query.replace(pos, 1, "`");
    }
    while ((pos = query.find('`')) != std::string::npos){
        query.replace(pos,1,"\'\'");
    }
}
void user(){
    QTextStream consoleInput(stdin);
    QSqlQuery query;
    int maxim =30;
    int numCols;
    QString requests[5] = {
        "SELECT \"Группы\".\"Номер_группы\",\"Факультеты\".\"Название\"\
        FROM Группы\
        join \"Факультеты\" on \"Факультеты\".\"ID_факультета\" = \"Группы\".\"ID_факультета\"",

        "SELECT \"Название\", \"ФИО\", \"Дата_рождения\"\
        FROM \"Факультеты\" f JOIN \"Группы\" g ON f.\"ID_факультета\" = g.\"ID_факультета\"\
        JOIN \"Студенты\" s ON g.\"Номер_группы\" = s.\"Группа\"",

        "SELECT \"Студенты\".\"ФИО\", \"Предприятия\".\"Название\", \
        \"Трудовые_договоры\".\"Дата_начала_практики\", \"Трудовые_договоры\".\"Дата_окончания_договора\"\
        FROM \"Студенты\"\
        JOIN \"Трудовые_договоры\" ON \"Студенты\".\"Серия_и_номер_паспорта\" = \"Трудовые_договоры\".\"Паспортные_данные_студента\"\
        JOIN \"Предприятия\" ON \"Трудовые_договоры\".\"Код_предприятия\" = \"Предприятия\".\"ID_предприятия\"",

        "SELECT \"Название\", COUNT(\"Серия_и_номер_паспорта\") AS \"Количество_студентов\"\
        FROM \"Факультеты\"\
        JOIN \"Группы\" ON \"Факультеты\".\"ID_факультета\" = \"Группы\".\"ID_факультета\"\
        JOIN \"Студенты\" ON \"Группы\".\"Номер_группы\" = \"Студенты\".\"Группа\"\
        GROUP BY \"Название\"",

        "select \"Студенты\".\"ФИО\" from \"Студенты\"\
        where \"Студенты\".\"Серия_и_номер_паспорта\" not in (\
        select \"Трудовые_договоры\".\"Паспортные_данные_студента\"\
        from \"Трудовые_договоры\")"
    };
    QString requests_text[5] = {
        "Вывод факультета у каждой группы",
        "Вывод факультетов и имена студентов",
        "Место практики студента",
        "Количество студентов на факультетах",
        "Неработающие студенты"
    };

    qDebug() << "what request do you want to execute?";

    for(int j=0;j<5;j++){
        qDebug() << j << ": "<< requests_text[j];
    }

    int request_index = -1;
    while (request_index <0 || request_index >= 5){
        qDebug() << "Enter the number of request:";
        consoleInput >> request_index;
    }
    if (query.exec(requests[request_index])) {
        QString row= "";
        QSqlRecord record = query.record();
        numCols = record.count();
        for (int i = 0; i < record.count(); i++) {
            QString columnName = record.fieldName(i);
            //qDebug() << columnName.leftJustified(maxim, ' ');
            row +=columnName.leftJustified(maxim, ' ');
        }
        qDebug() << qPrintable(row);

    } else {
        qDebug() << "Query failed: " << query.lastError().text();
    }
    //query.exec(requests[request_index]);
    //QSqlRecord record = query.record();
    //numCols = record.count();
    while (query.next()) {
        QString row = "";
        for (int i = 0; i < numCols; i++) {
            QString value = query.value(i).toString();
            row += value.leftJustified(maxim, ' ');
        }
        qDebug() << qPrintable(row);
    }

}
void admin(){
    QTextStream consoleInput(stdin);
    QSqlQuery query;
    query.exec("select table_name from information_schema.tables where table_schema='public' order by table_name");
    QVector<QString> tableNames;
    int i=0;
    while (query.next()) {
        QString tableName = query.value(0).toString();
        tableNames.push_back(tableName);
        qDebug() <<i<<": "<< tableName;
        i++;
    }

    int tableIndex = -1;
    while (tableIndex <0 || tableIndex >= tableNames.size()){
        qDebug() << "Enter the index of the table to add value:";
        consoleInput >> tableIndex;
    }

    QString selectedTable = tableNames.at(tableIndex);

    query.exec("SELECT column_name,data_type\
                FROM information_schema.columns\
                WHERE table_name = '"+selectedTable+"'");
    QVector<QString> tableColumns;
    QVector<QString> dataTypes;
    int numCols = 0;
    QString row;
    QString rowOfTypes;
    int maxim=40;
    while (query.next()) {
        //qDebug() << "Enter the index of the table to add value:";
        QString tableColumn = query.value(0).toString();
        QString dataType = query.value(1).toString();
        if (maxim<tableColumn.length()+4){maxim = tableColumn.length()+4;}
        tableColumns.push_back(tableColumn);
        dataTypes.push_back(dataType);
        row +=tableColumn.leftJustified(maxim, ' ');
        rowOfTypes+=dataType.leftJustified(maxim, ' ');
        numCols++;
    }
    qDebug() << qPrintable(row);
    qDebug() << qPrintable(rowOfTypes);

    query.exec("select * from \""+selectedTable+"\"");

    while (query.next()){
        row = "";
        for (int i = 0; i < numCols; i++) {
            QString column = query.value(i).toString();
            //qDebug()<< column << "\t";
            if (maxim<column.length()+4){maxim = column.length()+4;}
            row +=column.leftJustified(maxim, ' ');
        }
        qDebug() << qPrintable(row);
    }

    QVector<QString> values;
    for (int i = 0; i < tableColumns.size(); i++) {
        bool flag = false;
        QString value;
        while (not flag){
            qDebug() << "Enter value for " << tableColumns[i] << ": ";
            //consoleInput >> value;
            std::string input;
            std::getline(std::cin,input);
            correctApostrof(input);
            value = QString::fromStdString(input);

            if (dataTypes[i] == "bigint" or dataTypes[i]=="integer"){
                if (isNumeric(value)==true) flag= true;
            }
            else if(dataTypes[i] == "date"){
                if (isDate(value)==true) flag = true;
            }
            else{
                flag = true;
            }
        }
        values.push_back(value);
    }

    QString insertStatement = "INSERT INTO \"" + selectedTable + "\" (";
    for (int i = 0; i < tableColumns.size(); i++) {
        insertStatement += "\"" + tableColumns[i] + "\"";
        if (i < tableColumns.size() - 1) {
            insertStatement += ", ";
        }
    }
    insertStatement += ") VALUES (";
    for (int i = 0; i < values.size(); i++) {
        if (dataTypes[i].startsWith("int") || dataTypes[i].startsWith("numeric")) {
            insertStatement += values[i];
        } else {
            insertStatement += "'" + values[i] + "'";
        }
        if (i < values.size() - 1) {
            insertStatement += ", ";
        }
    }
    insertStatement += ")";

    if (query.exec(insertStatement)) {
        qDebug() << "Row added successfully.";
    } else {
        qDebug() << "Error adding row:" << query.lastError().text();
    }
}
int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);
    QTextStream consoleInput(stdin);
    QSqlDatabase db = QSqlDatabase::addDatabase("QPSQL");
    db.setHostName("localhost");
    db.setPort(5432);
    db.setDatabaseName("rabota_students");

    while (true){
        QString login;
        QString password;
        qDebug() << "Enter the login ";
        consoleInput >> login;
        qDebug() << "Enter the password ";
        consoleInput >> password;
        if (login == "root" and password == "123456"){
            db.setUserName("root");
            db.setPassword("123456");
            if (!db.open())
                qDebug() << db.lastError().text();
            else
                qDebug() << "All is good!\n";
            admin();
        }
        else if (login == "user" and password == "123456"){
            db.setUserName("user");
            db.setPassword("123456");
            if (!db.open())
                qDebug() << db.lastError().text();
            else
                qDebug() << "All is good!\n";
            user();
        }
        else{
            qDebug() << "Wrong the login or password ";
        }
    }

    db.close();
    return 0;
}
