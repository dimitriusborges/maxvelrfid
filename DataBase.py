import sqlite3
from pathlib import Path

db_name = 'veiculos.db'


class DataBase:

    def __init__(self):
        """

        """

        file = Path(db_name)

        if not file.is_file():
            # creates the db and its tables
            self.con = sqlite3.connect(db_name)
            self.cursor = self.con.cursor()

            self.create_table_veiculos()
            self.create_table_infracoes()
            self.create_table_leitoras()

            self.con.close()

    def open_con(self):
        self.con = sqlite3.connect(db_name)
        self.cursor = self.con.cursor()

    def close_con(self):
        self.con.close()

    def create_table_veiculos(self):

        self.cursor.execute(
            """
            CREATE TABLE veiculos(
            placa TEXT NOT NULL PRIMARY KEY,
            tag TEXT NOT NULL);
            """
        )

    def create_table_infracoes(self):

        self.cursor.execute(
            """
            CREATE TABLE infracoes(
            placa TEXT NOT NULL,
            tag TEXT NOT NULL,
            infr TEXT NOT NULL,
            FOREIGN KEY(placa) REFERENCES veiculos(placa));
            """
        )

    def create_table_leitoras(self):

        self.cursor.execute(
            """
            CREATE TABLE leitoras(
            nome TEXT NOT NULL PRIMARY KEY,
            IP TEXT NOT NULL,
            porta TEXT NOT NULL,
            antena TEXT NOT NULL);
            """
        )

    def insert_into_leitoras(self, nome, ip, porta, antena):

        comando = "INSERT INTO leitoras (nome, ip, porta, antena) VALUES(?,?,?, ?)"
        dados = nome, ip, porta, antena

        try:
            self.cursor.execute(comando, dados)
        except sqlite3.IntegrityError:
            return 0

        self.con.commit()

    def update_leitora(self, nome, ip, porta, antenas):
        """

        :param nome:
        :param ip:
        :param porta:
        :return:
        """

        command = "UPDATE leitoras set ip = (?), porta = (?), antena = (?) WHERE nome = (?)"
        dados = (ip, porta, antenas, nome)
        self.cursor.execute(command, dados)
        self.con.commit()

    def read_leitoras(self, nome=None):

        if nome is None:
            comando = "SELECT * FROM leitoras"
            self.cursor.execute(comando)
        else:
            comando = "SELECT * FROM leitoras WHERE nome = (?)"
            dados = nome
            self.cursor.execute(comando, [dados])

        return self.cursor.fetchall()

    def insert_into_veiculos(self, placa, tag):

        comando = "INSERT INTO veiculos (placa, tag) VALUES (?,?)"
        dados = placa, tag

        try:
            self.cursor.execute(comando, dados)
        except sqlite3.IntegrityError:
            return 0

        self.con.commit()

    def update_veiculos(self, placa, tag):

        command = "UPDATE veiculos SET tag = (?) WHERE placa = (?)"
        dados = tag, placa

        self.cursor.execute(command, dados)
        self.con.commit()

    def read_veiculos(self, placa=None, tag=None):

        if placa is None and tag is None:
            comando = "SELECT * FROM veiculos"
            self.cursor.execute(comando)

        elif placa is not None:
            comando = "SELECT * FROM veiculos WHERE placa = (?)"
            dados = placa
            self.cursor.execute(comando, [dados])

        elif tag is not None:
            comando = "SELECT * FROM veiculos WHERE tag = (?)"
            dados = tag
            self.cursor.execute(comando, [dados])

        return self.cursor.fetchall()

    def insert_into_infracoes(self, placa, tag, infr):

        comando = "INSERT INTO infracoes (placa, tag, infr) VALUES (?,?, ?)"
        dados = placa, tag, infr

        self.cursor.execute(comando, dados)
        self.con.commit()

    def read_infracoes(self, placa=None):

        if placa is None:
            self.cursor.execute("SELECT * FROM infracoes")
        else:
            comando = "SELECT * FROM infracoes WHERE placa = (?)"
            dados = placa
            self.cursor.execute(comando, [dados])

        return self.cursor.fetchall()

    def list_tables(self):
        """

        :return:
        """

        self.cursor.execute("SELECT name from sqlite_master WHERE type='table';")

        return self.cursor.fetchall()


if __name__ == "__main__":

    db = DataBase()
    db.open_con()
    
    db.close_con()
