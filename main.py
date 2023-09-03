import datetime
import os

import psycopg2
from psycopg2 import sql

from config import dbname,user,password,host
#from stud import *

def date_bug(data):
    return [item.strftime('%d.%m.%Y') if isinstance(item, datetime.date) else item for item in data]
class Table:
    def __init__(self, name, cursor):
        self.cursor = cursor
        self.name = name
        self.column_types = []
        self.columns = self.get_columns()
        self.primary_key = self.get_primary_key()
        self.data = self.get_data()
        self.foreign_column_names = None
        self.foreign_column_values = None
        self.column_name_of_foreign_key = None
        self.foreign_keys = self.get_foreign_keys()

    def get_columns(self):
        query = "\
            SELECT column_name, data_type\
            FROM information_schema.columns\
            WHERE table_name = %s"
        self.cursor.execute(query,(self.name,))
        columns = self.cursor.fetchall()
        for column in columns:
            data_type = column[1]
            if data_type == 'integer':
                python_type = int
            elif data_type == 'bigint':
                python_type = int
            elif data_type == 'smallint':
                python_type = int
            elif data_type == 'character varying':
                python_type = str
            elif data_type == 'text':
                python_type = str
            elif data_type == 'boolean':
                python_type = bool
            elif data_type == 'date':
                python_type = datetime.datetime
            elif data_type == 'numeric':
                python_type = float
            else:
                python_type = str
            self.column_types.append(python_type)
        return [column[0] for column in columns]

    def get_primary_key(self):
        query = "\
            SELECT column_name \
            FROM information_schema.columns \
            WHERE table_name = %s \
            AND column_default IS NULL \
            AND is_nullable = 'NO' \
            LIMIT 1"
        self.cursor.execute(query,(self.name,))
        primary_key = self.cursor.fetchone()[0]
        #primary_key = [key[0] for key in self.cursor.fetchall()]
        return primary_key
    def get_data(self):
        #self.cursor.execute(f"SELECT {', '.join(self.columns)} FROM \"{self.name}\" order by {self.primary_key}")
        query = sql.SQL("select {} from {} order by {} ASC").format(
            sql.SQL(', ').join(map(sql.Identifier, self.columns)),
            sql.Identifier(self.name),
            sql.Identifier(self.primary_key)
        )

        self.cursor.execute(query)
        data = self.cursor.fetchall()
        data = [date_bug(row) for row in data]
        return data
    def get_foreign_keys(self):
        query = "\
            SELECT ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name\
            FROM information_schema.table_constraints tc\
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name\
            JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name\
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;"
        self.cursor.execute(query,(self.name,))
        temp = self.cursor.fetchall()
        self.foreign_column_names = [foreign_key_name[1] for foreign_key_name in temp]
        object_value = []
        for i in range(len(self.foreign_column_names)):
            query = sql.SQL("select {} from {}").format(
                sql.Identifier(self.foreign_column_names[i]),
                sql.Identifier(temp[i][0])
            )
            self.cursor.execute(query)
            object_value.append([value[0] for value in self.cursor.fetchall()])
        self.foreign_column_values = object_value
        query = "SELECT column_name\
        FROM information_schema.columns\
        WHERE table_name = %s AND column_name IN (\
            SELECT column_name\
            FROM information_schema.key_column_usage\
            WHERE table_name = %s AND constraint_name IN (\
                SELECT constraint_name\
                FROM information_schema.table_constraints\
                WHERE table_name = %s AND constraint_type = 'FOREIGN KEY'\
            )\
        );\
        "
        self.cursor.execute(query,(self.name,self.name,self.name,))
        self.column_name_of_foreign_key = [column[0] for column in self.cursor.fetchall()]
        return [foreign_key[0] for foreign_key in temp]
def try_execute(query, values,cursor):
    try:
        cursor.execute(query,values)
        return True
    except Exception as e:
        print('Error:', e)
        return False
def try_input(str,action = 'int'):
    try:
        n = input(str)
        if action == 'int': n = int(n)
        return n
    except Exception as e:
        print('Error:', e)
        return '-1'
class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.tables = None

    def connect(self,user = user, password = password):
        try:
            if self.conn is not None:
                self.cursor.close()
                self.conn.commit()
                self.conn.close()
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host)
            self.cursor = self.conn.cursor()
            self.tables = self.get_tables()
        except psycopg2.OperationalError as e:
            print("Ошибка подключения к базе данных: ", e)

    def __del__(self):
        if self.conn is not None:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
    def get_tables(self):
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
            ORDER BY table_name""")
        table_names = [table_name[0] for table_name in self.cursor.fetchall()]
        table_objects = []
        for table_name in table_names:
            table_object = Table(table_name,self.cursor)
            table_objects.append(table_object)
        return table_objects
    def print_table(self, table):
        print(table.columns)
        for i, row in enumerate(table.data):
            print(f'{i}: {row}')
    def correction_type(self,table,column):
        flag = False
        while not flag:
            value = input(f'Введите значение для столбца "{column}": ')
            try:
                if table.column_types[table.columns.index(column)] == datetime.datetime:
                    value = datetime.datetime.strptime(value, '%d.%m.%Y')
                else:
                    #print(table.column_types[table.columns.index(column)])
                    value = table.column_types[table.columns.index(column)](value)
            except Exception as e:
                print('Error:', e)
                #print('это функция correction_type')
                #print(type(value),table.column_types[table.columns.index(column)])
            if type(value) == table.column_types[table.columns.index(column)]:
                flag = True
        return value
    def check_foreign_keys(self, table, column):
        flag = False
        while not flag:
            value = self.correction_type(table,column)
            for i in range(len(table.column_name_of_foreign_key)):
            #i = table.column_name_of_foreign_key.index(column)
                #print(i,value,table.foreign_column_values[i])
                if value in table.foreign_column_values[i]:
                    flag = True
        return value
    def com_print(self,action='None'):
        os.system('cls')
        maxim = 0
        for i, table in enumerate(self.tables):
            print(f"{i}: {table.name}")
            maxim = i
        str = 'Введите номер таблицы\n'
        n = try_input(str)
        if n=='-1':
            return
        elif n > maxim:
            print('Ошибка ввода')
        else:
            os.system('cls')
            self.print_table(self.tables[n])
            if action == 'record':
                self.com_record(self.tables[n])
            elif action == 'delete':
                self.com_delete(self.tables[n])
            elif action == 'edit':
                self.com_edit(self.tables[n])
    def com_record(self,table):
        columns = table.columns
        values = []
        for i in range(len(table.foreign_keys)):
            print(i,table.foreign_column_names[i])
            print(i,table.foreign_column_values[i])
        for column in columns:
            if column in table.column_name_of_foreign_key:
                value = self.check_foreign_keys(table,column)
                values.append(value)
            else:
                value = self.correction_type(table,column)
                values.append(value)
            
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table.name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )

        flag = try_execute(query, tuple(values),self.cursor)
        if flag:
            print('Запись добавлена')
            input('Перейти далее')
            os.system('cls')
            return
        else:
            print('Не удалось добавить запись')
            input('Выйти в гланое меню')
            os.system('cls')
            return
    def com_delete(self,table):
        str = 'Какое значение удалить: '
        i = try_input(str,'int')
        if i == '-1':
            input('Выйти в гланое меню')
            os.system('cls')
            return
        else:
            query = sql.SQL("DELETE FROM {} WHERE {} IN (SELECT {} FROM {} LIMIT 1 OFFSET %s)").format(
                sql.Identifier(table.name),
                sql.Identifier(table.primary_key),
                sql.Identifier(table.primary_key),
                sql.Identifier(table.name)
            )
            flag = try_execute(query, (i,),self.cursor)

            if flag:
                print('Запись удалена')
                input('Перейти далее')
                os.system('cls')
                return
            else:
                print('Не удалось удалить запись')
                input('Перейти далее')
                os.system('cls')
                return
    def com_edit(self,table):
        str = 'Какое значение хотите изменить: '
        i = try_input(str)
        if  i == '-1':
            input('Выйти в гланое меню')
            os.system('cls')
            return
        else:
            os.system('cls')
            data = table.data
            values = []
            for column in table.columns:
                if column in table.column_name_of_foreign_key:
                    value = self.check_foreign_keys(table,column)
                else:
                    value = self.correction_type(table,column)
                values.append(value)
            query = sql.SQL("UPDATE {} SET {} WHERE {} = %s").format(
                sql.Identifier(table.name), 
                sql.SQL(', ').join(sql.SQL(f"{col} = %s") for col in table.columns), 
                sql.Identifier(table.primary_key)
            )

            flag = try_execute(query,tuple(values + [data[i][0]]),self.cursor)
            if flag:
                print('Запись изменена')
                input('Перейти далее')
                os.system('cls')
                return
            else:
                print('Не удалось изменить запись')
                input('Перейти далее')
                os.system('cls')
                return

if __name__ == '__main__':
    db = Database()
    db.connect()
    while True:
        string = 'Какую команду хотите выполнить?(print,record,delete,edit,exit)\n'   
        action = try_input(string,'str')
        if action in  ['print','record','delete','edit']:
            db.com_print(action)
        elif action == 'exit':
            break
