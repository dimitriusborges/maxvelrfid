import random
import time
from tkinter import *
from tkinter import ttk
from Application import Application
from tkinter import messagebox
import threading
from collections import Counter
import matplotlib as plt; plt.rcdefaults()
import matplotlib.pyplot as plt


class CadastroVeiculo:

    def __init__(self, master):

        self.this = Toplevel(master)
        self.this.title("Cadastro")
        self.this.resizable(False, False)

        w = self.this.winfo_screenwidth()
        h = self.this.winfo_screenheight()

        x = (w - self.this.winfo_reqwidth()) / 2
        y = (h - self.this.winfo_reqheight()) / 2

        self.this.geometry("+%d+%d" % (x-150, y-150))

        self.carros_cadastrados = []
        self.leitora = ['leitora', '127.0.0.1', '20000']
        self.app = Application()

    def build_window(self):
        """

        :return:
        """

        main_frame = Frame(self.this)
        main_frame.pack()

        lbl_leitora = Label(main_frame, text="Leitora:")
        lbl_leitora.grid(row=0, column=0, pady=20, padx=10, sticky='w')

        self.leitoras = ttk.Combobox(main_frame, width=20)
        self.leitoras.grid(row=0, column=1, pady=20, columnspan=3, sticky='w')

        lbl_lista = Label(main_frame, text="Tags detectadas:")
        lbl_lista.grid(row=1, column=0)

        self.list_box = Listbox(main_frame, width=50, height=10)
        self.list_box.grid(row=2, column=0, columnspan=4, padx=10, pady=5)
        self.list_box.bind('<Double-Button-1>', self.load_tag)

        bt_refresh = Button(main_frame, width=10, text="Atualizar", command=self.popular_lista)
        bt_refresh.grid(row=2, column=4, padx=10)

        lbl_tag = Label(main_frame, text="Tag selecionada:")
        lbl_tag.grid(row=3, column=0, columnspan=2)

        self.tag = Entry(main_frame, width=30)
        self.tag.grid(row=3, column=2, columnspan=2, padx=10, pady=5, sticky='w')
        self.tag.config(state='readonly')

        lbl_placa = Label(main_frame, text="Placa do veículo:")
        lbl_placa.grid(row=4, column=0, columnspan=2)

        self.placa = Entry(main_frame, width=10)
        self.placa.grid(row=4, column=2, columnspan=2, padx=10, sticky='w')

        bt_cadastrar = Button(main_frame, width=10, text="Cadastrar", command=self.cadastrar_veiculo)
        bt_cadastrar.grid(row=5, column=0, padx=10, pady=10, sticky='w')

        bt_limpar = Button(main_frame, width=10, text="Limpar")
        bt_limpar.grid(row=5, column=2, padx=10, pady=10, sticky='e')

        bt_cancelar = Button(main_frame, width=10, text="Cancelar", command=self.close_window)
        bt_cancelar.grid(row=5, column=4, padx=10, pady=10, sticky='e')

        self.tabela_carros = ttk.Treeview(main_frame, selectmode="browse", show='headings')

        ttk.Style().configure("Treeview", width=50)

        self.tabela_carros['columns'] = '1', '2'

        self.tabela_carros.column('#1', width='100')
        self.tabela_carros.heading('#1', text='Placa')

        self.tabela_carros.column('#2', width='300')
        self.tabela_carros.heading('#2', text='Tag RFID')

        self.tabela_carros.grid(row=6, column=0, columnspan=5, padx=5, pady=10)

        scroll_bar_tree_vertical = Scrollbar(main_frame, relief='flat')
        scroll_bar_tree_vertical.grid(row=6, column=6, sticky=('w', 'e', 'n', 's'))

        self.tabela_carros.config(yscrollcommand=scroll_bar_tree_vertical.set)
        scroll_bar_tree_vertical.config(command=self.tabela_carros.yview)

        self.tabela_carros.bind('<Double-Button-1>', self.load_da_tabela)

        self.popular_tabela()
        self.popular_box()

    def open_window(self):
        self.build_window()
        self.this.mainloop()

    def close_window(self):
        self.this.destroy()

    def popular_lista(self):

        self.list_box.delete(0, END)

        if len(self.leitoras.get()) == 0:
            messagebox.showwarning("Erro", "Antes, escolha uma leitora!", parent=self.this)
            return

        leitora = self.app.get_leitoras_registradas(self.leitoras.get())[0]

        tags = self.app.ler_tags(leitora[1], leitora[2])

        for tag in tags:
            self.list_box.insert(END, tag)

    def popular_tabela(self):

        if len(self.tabela_carros.get_children()) > 0:
            self.tabela_carros.delete(*self.tabela_carros.get_children())

        self.carros_cadastrados = self.app.get_veiculos_reg()

        row = 0
        for registro in self.carros_cadastrados:

            self.tabela_carros.insert("", row, iid=str(row), values=[registro[0], registro[1]])

            row += 1

    def popular_box(self):
        """

        :return:
        """

        readers = self.app.get_leitoras_registradas()

        if len(readers) == 0:
            self.leitoras.config(state='readonly')
            return

        names = [reader[0] for reader in readers]

        self.leitoras.config(state='normal')
        self.leitoras.config(value=names)
        self.leitoras.config(state='readonly')

    def cadastrar_veiculo(self):

        if len(self.tag.get()) == 0 or len(self.placa.get()) == 0:
            messagebox.showwarning("Erro", "Antes, preencha todos os campos corretamente", parent=self.this)
            return

        tag = self.tag.get()
        placa = self.placa.get()

        try:
            self.app.registrar_veiculo(placa, tag)
        except:
            op = messagebox.askyesno("Erro", "Esse veiculo já possui uma tag cadastrada, deseja atualizar?", parent=self.this)

            if op is True:
                self.app.atualizar_tag_veiculo(placa, tag)

            else:
                self.clear_entries()
                return

        messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!", parent=self.this)
        self.popular_tabela()

        self.clear_entries()

    def load_tag(self, event):

        self.tag.config(state="normal")
        self.tag.delete(0, END)
        self.tag.insert(0, self.list_box.get(self.list_box.curselection()))
        self.tag.config(state="readonly")

    def load_da_tabela(self, event):
        """

        :param event:
        :return:
        """

        index = int(self.tabela_carros.selection()[0])

        carro = self.carros_cadastrados[index]

        self.placa.delete(0, END)
        self.placa.insert(0, carro[0])

        self.tag.config(state="normal")
        self.tag.delete(0, END)
        self.tag.insert(0, carro[1])
        self.tag.config(state="readonly")

    def clear_entries(self):

        self.tag.config(state="normal")
        self.tag.delete(0, END)
        self.tag.config(state="readonly")
        self.placa.delete(0, END)


class CadastroLeitora:

    def __init__(self, master):

        self.this = Toplevel(master)
        self.this.title("Cadastro")
        self.this.resizable(False, False)

        w = self.this.winfo_screenwidth()
        h = self.this.winfo_screenheight()

        x = (w - self.this.winfo_reqwidth()) / 2
        y = (h - self.this.winfo_reqheight()) / 2

        self.this.geometry("+%d+%d" % (x-150, y-150))

        self.app = Application()

        self.leitoras_cadastradas = []

    def build_window(self):
        """

        :return:
        """

        main_frame = Frame(self.this)
        main_frame.pack()

        lbl_nome = Label(main_frame, text="Nome para leitora:")
        lbl_nome.grid(row=2, column=0, columnspan=2, sticky='w')

        self.leitora = Entry(main_frame, width=15)
        self.leitora.grid(row=2, column=2, columnspan=2, padx=10, pady=5, sticky='w')

        lbl_ip = Label(main_frame, text="Ip de acesso:")
        lbl_ip.grid(row=3, column=0, columnspan=2, sticky='w')

        self.ip = Entry(main_frame, width=20)
        self.ip.grid(row=3, column=2, columnspan=2, padx=10, pady=5, sticky='w')

        lbl_porta = Label(main_frame, text="Porta:")
        lbl_porta.grid(row=4, column=0, columnspan=2, sticky='w')

        self.porta = Entry(main_frame, width=10)
        self.porta.grid(row=4, column=2, columnspan=2, padx=10, pady=5, sticky='w')

        lbl_antenas = Label(main_frame, text="Nº Antenas:")
        lbl_antenas.grid(row=5, column=0, columnspan=2, sticky='w')

        self.antenas = Spinbox(main_frame, width=3, from_=1, to=4)
        self.antenas.grid(row=5, column=2, columnspan=2, padx=10, pady=5, sticky='w')
        self.antenas.config(state='readonly')

        bt_cadastrar = Button(main_frame, width=10, text="Cadastrar", command=self.cadastar_leitora)
        bt_cadastrar.grid(row=10, column=0, padx=10, pady=10, sticky='w')

        bt_limpar = Button(main_frame, width=10, text="Limpar", command=self.clear_entries())
        bt_limpar.grid(row=10, column=2, padx=10, pady=10, sticky='e')

        bt_cancelar = Button(main_frame, width=10, text="Cancelar", command=self.close_window)
        bt_cancelar.grid(row=10, column=4, padx=10, pady=10, sticky='e')

        self.tabela_leitoras = ttk.Treeview(main_frame, selectmode="browse", show='headings')

        ttk.Style().configure("Treeview", width=50)

        self.tabela_leitoras['columns'] = '1', '2', '3', '4'

        self.tabela_leitoras.column('#1', width='100')
        self.tabela_leitoras.heading('#1', text='Nome')

        self.tabela_leitoras.column('#2', width='200')
        self.tabela_leitoras.heading('#2', text='IP')

        self.tabela_leitoras.column('#3', width='100')
        self.tabela_leitoras.heading('#3', text='Porta')

        self.tabela_leitoras.column('#4', width='100')
        self.tabela_leitoras.heading('#4', text='Nº Antenas')

        self.tabela_leitoras.grid(row=6, column=0, columnspan=5, padx=5, pady=10)

        self.tabela_leitoras.bind('<Double-Button-1>', self.load_da_tabela)

        scroll_bar_tree_vertical = Scrollbar(main_frame, relief='flat')
        scroll_bar_tree_vertical.grid(row=6, column=6, sticky=('w', 'e', 'n', 's'))

        self.tabela_leitoras.config(yscrollcommand=scroll_bar_tree_vertical.set)
        scroll_bar_tree_vertical.config(command=self.tabela_leitoras.yview)

        self.popular_tabela()

    def cadastar_leitora(self):

        if len(self.leitora.get()) == 0 or len(self.ip.get()) == 0 or len(self.porta.get()) == 0:
            messagebox.showwarning("Erro", "Antes, preencha todos os campos corretamente", parent=self.this)
            return

        nome = self.leitora.get()
        ip = self.ip.get()
        porta = self.porta.get()
        antenas = self.antenas.get()

        try:
            self.app.registrar_leitora(nome, ip, porta, antenas)

        except:

            op = messagebox.askyesno("Erro", "Essa leitora já possui um registro, deseja atualizar?", parent=self.this)

            if op is True:
                self.app.atualizar_leitora(nome, ip, porta, antenas)
            else:
                self.clear_entries()
                return

        self.app.conf_antenas(ip, porta, int(antenas))
        messagebox.showinfo("Cadastro", "Cadastro realizado com sucesso!", parent=self.this)

        self.popular_tabela()

        self.clear_entries()

    def popular_tabela(self):
        """

        :return:
        """

        if len(self.tabela_leitoras.get_children()) > 0:
            self.tabela_leitoras.delete(*self.tabela_leitoras.get_children())

        self.leitoras_cadastradas = self.app.get_leitoras_registradas()

        row = 0
        for registro in self.leitoras_cadastradas:

            self.tabela_leitoras.insert("", row, iid=int(row), values=[registro[0], registro[1], registro[2], registro[3]])

            row += 1

    def load_da_tabela(self, event):
        """

        :param event:
        :return:
        """

        index = int(self.tabela_leitoras.selection()[0])

        carro = self.leitoras_cadastradas[index]

        self.leitora.delete(0, END)
        self.leitora.insert(0, carro[0])

        self.ip.delete(0, END)
        self.ip.insert(0, carro[1])

        self.porta.delete(0, END)
        self.porta.insert(0, carro[2])

    def clear_entries(self):
        """

        :return:
        """

        self.leitora.delete(0, END)
        self.ip.delete(0, END)
        self.porta.delete(0, END)

    def open_window(self):
        self.build_window()
        self.this.mainloop()

    def close_window(self):
        self.this.destroy()


class Registros:

    def __init__(self, master):

        self.this = Toplevel(master)
        self.this.title("Registros")
        self.this.resizable(False, False)

        w = self.this.winfo_screenwidth()
        h = self.this.winfo_screenheight()

        x = (w - self.this.winfo_reqwidth()) / 2
        y = (h - self.this.winfo_reqheight()) / 2

        self.this.geometry("+%d+%d" % (x-150, y-150))

        self.app = Application()

        self.infracoes_cadastradas = []

    def build_window(self):
        """

        :return:
        """

        main_frame = Frame(self.this)
        main_frame.pack()

        self.tabela_registros = ttk.Treeview(main_frame, selectmode="browse", show='headings')

        ttk.Style().configure("Treeview", width=50)

        self.tabela_registros['columns'] = '1', '2', '3'

        self.tabela_registros.column('#1', width='100')
        self.tabela_registros.heading('#1', text='Placa')

        self.tabela_registros.column('#2', width='200')
        self.tabela_registros.heading('#2', text='Tag')

        self.tabela_registros.column('#3', width='100')
        self.tabela_registros.heading('#3', text='Infração')

        self.tabela_registros.grid(row=5, column=0, columnspan=5, padx=5, pady=10)

        scroll_bar_tree_vertical = Scrollbar(main_frame, relief='flat')
        scroll_bar_tree_vertical.grid(row=5, column=6, sticky=('w', 'e', 'n', 's'))

        self.tabela_registros.config(yscrollcommand=scroll_bar_tree_vertical.set)
        scroll_bar_tree_vertical.config(command=self.tabela_registros.yview)

        self.popular_tabela()

    def popular_tabela(self):
        """

        :return:
        """

        if len(self.tabela_registros.get_children()) > 0:
            self.tabela_registros.delete(*self.tabela_registros.get_children())

        self.infracoes_cadastradas = self.app.get_infracoes()

        row = 0
        for registro in self.infracoes_cadastradas:

            self.tabela_registros.insert("", row, iid=int(row), values=[registro[0], registro[1], registro[2]])

            row += 1

    def open_window(self):
        self.build_window()
        self.this.mainloop()

    def close_window(self):
        self.this.destroy()


class TelaPrincipal:

    def __init__(self):
        """
        """

        self.root = Tk()
        self.root.title("Radar RFID")
        self.root.resizable(False, False)

        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()

        x = (w - self.root.winfo_reqwidth()) / 2
        y = (h - self.root.winfo_reqheight()) / 2

        self.root.geometry("+%d+%d" % (x-200, y-200))

        self.app = Application()

        self.thread_radar = threading.Thread(target=self.start_radar)
        self.thread_radar.setDaemon(True)

        self.thread_grafico = threading.Thread(target=self.plot_grafico)
        self.thread_grafico.setDaemon(True)

    def open_window(self):

        self.build_window()
        self.root.mainloop()

    def build_window(self):
        """

        :return:
        """

        main_frame = Frame(self.root)
        main_frame.pack()

        # submenu
        upper_menu = Menu(self.root, relief='groove')

        self.root['menu'] = upper_menu

        sub_menu_cadastro = Menu(upper_menu)
        sub_menu_cadastro.add_command(label="Veículos", command=self.open_veiculos)
        sub_menu_cadastro.add_command(label="Leitoras", command=self.open_leitoras)
        upper_menu.add_cascade(menu=sub_menu_cadastro, label="Cadastro")

        sub_menu_registros = Menu(upper_menu)
        sub_menu_registros.add_command(label="Infrações", command=self.open_registros)
        upper_menu.add_cascade(menu=sub_menu_registros, label="Registros")

        img = PhotoImage(file='dummy.png')
        self.graf = Label(main_frame, image=img)
        self.graf.image = img
        self.graf.grid(row=1, column=0, columnspan=4)

        bt_iniciar = Button(main_frame, text="Iniciar", command=lambda: self.thread_radar.start())
        bt_iniciar.grid(row=0, column=3, padx=10, pady=5, sticky='e')

        # saida

        label_debugg = Label(main_frame, text="Detecções:")
        label_debugg.grid(row=9, column=0, pady=5, sticky='w')
        self.debugg = Text(main_frame, width=80, height=5)
        self.debugg.grid(row=10, column=0, columnspan=4, padx=10, pady=10)

    def open_veiculos(self):
        """

        :return:
        """
        janela_cadastro = CadastroVeiculo(self.root)
        janela_cadastro.open_window()

    def open_leitoras(self):
        """

        :return:
        """
        janela_leitoras = CadastroLeitora(self.root)
        janela_leitoras.open_window()

    def open_registros(self):
        """

        :return:
        """
        janela_reg = Registros(self.root)
        janela_reg.open_window()

    def start_radar(self):

        self.debugg.insert(CURRENT, "Iniciando Simulação...\n")

        while 1:

            output = self.app.execute_radar()

            if output is not None:
                self.debugg.insert(END, output)
                self.plot_grafico()

    def plot_grafico(self):

        infractions = self.app.get_infracoes()

        if len(infractions) > 0:
            infr_counter = Counter(elem[2] for elem in infractions)

            labels = list(infr_counter.keys())
            counters = list(infr_counter.values())
        else:
            labels = "Tipo 1", "Tipo 2", "tipo 3"
            counters = 0, 0, 0

        plt.clf()
        plt.bar(labels, counters, align='center', alpha=0.5, color='b')
        plt.ylabel('Nº Ocorrências')
        plt.xlabel('Tipo de Infração')
        plt.title("Frequência de Infrações")
        plt.savefig('plot.png', transparent=True)

        img = PhotoImage(file='plot.png')

        self.graf.image = img
        self.graf.config(image=img)
        self.graf.image = img


if __name__ == "__main__":
    gui = TelaPrincipal()
    gui.open_window()
