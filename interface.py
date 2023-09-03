import psycopg2
import datetime
import os
import threading
from config import dbname,user,password,host
from stud import *

class Table:
    def __init__(self, name, columns, primary_key):
        self.name = name
        self.columns = columns
        self.primary_key = primary_key
global my_thread
class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host)
        self.cursor = self.conn.cursor()
        self.tables = self.get_tables()
        self.db_thread = 0
        self.my_thread = threading.Thread(target=self.window, args=(self.tables[0],))
    def __del__(self):
        self.conn.close()
    def window(self,table):
        app = QApplication(sys.argv)
        ex = MyWidget(table)
        ex.show()
        app.exec_()
    def date_bug(self, data):
        return [item.strftime('%d.%m.%Y') if isinstance(item, datetime.date) else item for item in data]
    def get_table_columns(self, table):
        self.cursor.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table}'""")
        return [column[0] for column in self.cursor.fetchall()]
    def get_tables(self):
        self.cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema='public'
            ORDER BY table_name""")
        tables = [table[0] for table in self.cursor.fetchall()]
        table_objects = []
        for table in tables:
            columns = self.get_table_columns(table)
            self.cursor.execute(
                f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}' AND column_default IS NULL AND is_nullable = 'NO' LIMIT 1")
            primary_key = self.cursor.fetchone()[0]
            table_object = Table(table, columns, primary_key)
            table_objects.append(table_object)
        return table_objects
    def print_table(self, table):
        self.cursor.execute(f"SELECT {', '.join(table.columns)} FROM \"{table.name}\"")
        data = self.cursor.fetchall()
        data = [self.date_bug(row) for row in data]
        print(table.columns)
        for i, row in enumerate(data):
            print(f'{i}: {row}')
    def get_primary_key(self, table_name):
        self.cursor.execute(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND column_name IN (
                SELECT column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
                WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name = '{table_name}'
            )
        """)
        return self.cursor.fetchone()[0]
    def check_foreign_keys(self, table):
        self.cursor.execute(f"""
            SELECT ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table.name}';
        """)
        foreign_keys = self.cursor.fetchall()
        if foreign_keys:
            for key in foreign_keys:
                print('\n\n')
                self.print_table(Table(key[0], self.get_table_columns(key[0]), self.get_primary_key(key[0])))
    def try_execute(self,query, values):
        try:
            self.cursor.execute(query,values)
            return True
        except Exception as e:
            print('Error:', e)
            input('Выйти в гланое меню')
            os.system('cls')
            return False
    def try_input(self,str,action = 'int'):
        try:
            n = input(str)
            if action == 'int': n = int(n)
            return n
        except Exception as e:
            print('Error:', e)
            input('Выйти в гланое меню')
            return 0

    def com_print(self, action='None'):
        os.system('cls')
        maxim = 0
        for i, table in enumerate(self.tables):
            print(f"{i}: {table.name}")
            maxim = i
        str = 'Введите номер таблицы\n'
        #n = int(input(str))
        n = self.try_input(str)
        if n > i:
            print('Ошибка ввода')
        else:
            os.system('cls')
            if self.db_thread == 0:
                self.db_thread = 1   
                self.my_thread = threading.Thread(target=self.window, args=(self.tables[n],))
                self.my_thread.start()
            else:
                self.my_thread.join()
                self.db_thread = 0

            #self.print_table(self.tables[n])
            if action == 'record':
                self.com_record(self.tables[n])
            elif action == 'delete':
                self.com_delete(self.tables[n],maxim)
            elif action == 'edit':
                self.com_edit(self.tables[n],maxim)
            else:
                self.my_thread.join()
                self.db_thread = 0
    def com_record(self, table):
        self.check_foreign_keys(table)
        columns = table.columns
        values = []
        for column in columns:
            value = input(f'Введите значение для столбца "{column}": ')
            values.append(value)
        query = f"INSERT INTO {table.name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
        flag = self.try_execute(query,tuple(values))
        #self.cursor.execute(query, tuple(values))
        if flag:
            print('Запись добавлена')
            input('Перейти далее')
            self.com_print()
        else:
            print('Произошла ошибка')
    def com_delete(self, table,maxim):
        str = 'Какое значение удалить: '
        #i = int(input(str))
        i = self.try_input(str)
        if i>maxim:
            print('Ошибка ввода')
            input('В главное меню')
        else:
            query = f"DELETE FROM {table.name} WHERE {table.primary_key} IN (SELECT {table.primary_key} FROM {table.name} LIMIT 1 OFFSET %s)"
            #self.cursor.execute(query, (i,))
            flag = self.try_execute(query,(i,))
            if flag:
                print('Запись удалена')
                input('Перейти далее')
                self.com_print()
            else:
                print('Не удалось удалить запись')
                input('Перейти далее')
    def com_edit(self, table,maxim):
        str = 'Какое значение хотите изменить: '
        #i = int(input(str))
        i = self.try_input(str)
        if i>maxim:
            print('Ошибка ввода')
            input('В главное меню')
        else:
            self.cursor.execute(f"SELECT * FROM {table.name}")
            data = self.cursor.fetchall()
            values = [input(f'Введите новое значение для столбца "{column}": ') for column in table.columns]
            query = f"UPDATE {table.name} SET {', '.join([f'{col} = %s' for col in table.columns])} WHERE {table.primary_key} = %s"
            #self.cursor.execute(query, tuple(values + [data[i][0]]))
            flag = self.try_execute(query,tuple(values + [data[i][0]]))
            if flag:
                print('Запись изменена')
                input('Перейти далее')
                self.com_print()
            else:
                print('Не удалось изменить запись')
                input('Перейти далее')
    def connect(self):
        while True:
            str = 'Какую команду хотите выполнить?(print,record,delete,edit)\n'
            #action = input(str)
            action = self.try_input(str,'str')
            if action in  ['print','record','delete','edit']:
                self.com_print(action)

if __name__ == '__main__':
    db = Database()
    db.connect()
