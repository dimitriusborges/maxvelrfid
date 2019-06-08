import random
import time

from DataBase import DataBase
from Alien9000 import Alien9000

"""
(100 km/h) / 3.6 = 27,77 m/s -> 10 metros / 27,77 = 0,36s
(110 km/h) / 3.6 = 30,55 m/s -> 10 metros / 30,55= 0,32s

Formula geral:

(Distancia entre leitoras)
___________________________

Velocidade do veiculo / 3.6


10/(100/3.6) = 0.36s
10/(110/3.6) = 0.327s
"""

dummy_plates = ["OPI5504", "HND8023"]

readers_dist = 100   # meters, distance between the 2 readers to capture speed
max_speed = 100     # km/h, max speed allowed
max_time_span = readers_dist/(max_speed/3.6)   # seconds, max time a car can take to pass these 10 meters


class Application:

    def __init__(self):
        """

        """
        self.db = DataBase()
        self.a9 = Alien9000()

        self.prob_inf = [0.5, 0.5]
        self.inf_all_types = [20, 49, 100]
        self.prob_inf_type = [0.6, 0.3, 0.1]
        self.lower_bound = {
            20: 1,
            49: 21,
            100: 50,
        }

        self.l_registro = ["127.0.0.1", "20000"]  # reader to register vehicles
        self.l_posicao1 = ["127.0.0.1", "20001"]  # first reader for speed detector
        self.l_posicao2 = ["127.0.0.1", "20002"]  # second reader for speed detector

    def ler_tags(self, ip, porta):
        """
        Execute a single tag reading on reader at ip + port
        :param ip:  reader address
        :param porta: reader address
        :return:
        """

        self.a9.open_con(ip, porta)
        self.a9.login()

        tag_list, _ = self.a9.tag_read()

        self.a9.close_con()
        return tag_list

    def registrar_veiculo(self, placa, tag):
        """
        Register a rfid tag to a vehicle, associated to its plate
        :param placa: Vehicle plate
        :param tag: rfid tag
        :return:
        """

        self.db.open_con()

        if self.db.insert_into_veiculos(placa, tag) == 0:
            raise Exception("Registro já existe")

        self.db.close_con()

    def get_veiculos_reg(self):
        """

        :return:
        """

        self.db.open_con()

        registers = self.db.read_veiculos()

        self.db.close_con()

        return registers

    def atualizar_tag_veiculo(self, placa, tag):
        self.db.open_con()

        self.db.update_veiculos(placa, tag)

        self.db.close_con()

    def get_tags_reg(self):
        """
        get all tags registered on the data base
        :return:
        """

        self.db.open_con()

        registers = self.db.read_veiculos()

        tags = [register[1] for register in registers]

        self.db.close_con()

        return tags

    def registrar_infracao(self, tag, infr):
        """
        Register a velocity infraction associated to a vehicle
        :param plate: Vehicle plate
        :param infr: type of the infraction
        :return:
        """

        self.db.open_con()

        plate = (self.db.read_veiculos(tag=tag)[0])[0]

        self.db.insert_into_infracoes(plate, infr)

        self.db.close_con()

    def get_infracoes(self):

        self.db.open_con()
        result = self.db.read_infracoes()
        self.db.close_con()

        return result

    def registrar_leitora(self, nome, ip, porta):
        """
        """

        self.db.open_con()

        if self.db.insert_into_leitoras(nome, ip, porta) == 0:
            raise Exception("Registro já existe")

        self.db.close_con()

    def atualizar_leitora(self, nome, ip, porta):
        self.db.open_con()

        self.db.update_leitora(nome, ip, porta)

        self.db.close_con()

    def get_leitoras_registradas(self, nome=None):

        self.db.open_con()

        registers = self.db.read_leitoras(nome)

        self.db.close_con()

        return registers

    def execute_radar(self):
        """
        Routine to execute the radar function, read tag on the first reader and than on 2nd one to calculate the
        velocity. The velocity is "virtual", i.e., it is generated by a random function and associated to the time
        between reading on 1st and 2nd readers
        :return:
        """

        buffer_tags = []    # save tags red on the first reader

        generated_time = self.gerar_time_span()

        # no bad behavior generated, no reading
        if generated_time == 0:
            return None

        else:
            # get tag passed on 1st reader
            buffer_tags.append(self.ler_tags(self.l_posicao1[0], self.l_posicao1[1]))

            # velocity simulator
            start = time.time()
            time.sleep(generated_time)
            time_span = time.time() - start

            # get tag on 2nd reader
            captured_tag = self.ler_tags(self.l_posicao2[0], self.l_posicao2[1])

            # if a tag passed on both readers, it generated an infraction
            if captured_tag in buffer_tags:

                # Calcs the infraction size in percentage
                infraction = (1 - time_span / max_time_span) * 100
                infr_type = self.classificar_infr(infraction)

                infr_output = "Infraction {}. Car took {:.2} seconds to travel {} meters. Should be {}.\n".format(infr_type, time_span, readers_dist, max_time_span)

                self.registrar_infracao(captured_tag[0], infr_type)

                return infr_output

    def gerar_comportamento(self):
        """
        Random generates a bad behavior indicator, i.e., how much, in percentage, a car will be above the max permitted
        velocity.
        :return:
        """

        is_infr = random.choices([0, 1], self.prob_inf)[0]

        # No bad behavior generated
        if is_infr is 0:
            return 0

        # bad behavior
        else:
            infr_type = random.choices(self.inf_all_types, self.prob_inf_type)[0]

            lower_bound = self.lower_bound[infr_type]

            infr_size = random.choices(range(lower_bound, infr_type))[0]

            return infr_size

    def classificar_infr(self, infracao):
        """
        Classify the infraction in one of the three types from brazilian law
        :param infracao: size of the infraction, in %
        :return:
        """
        if self.lower_bound[self.inf_all_types[0]] <= infracao <= self.inf_all_types[0]:
            return "Tipo 1"
        elif self.lower_bound[self.inf_all_types[1]] <= infracao <= self.inf_all_types[1]:
            return "Tipo 2"
        elif self.lower_bound[self.inf_all_types[2]] <= infracao <= self.inf_all_types[2]:
            return "Tipo 3"

    def gerar_time_span(self):
        """
        Generates the time span necessarily between reading to emulate a speed infraction, associated to the time span
        necessarily to travel the gap between readers
        :return: How many seconds the car took to travel between readers. 0 means no infraction, i.e., <= max_speed
        """

        infr = self.gerar_comportamento()

        if infr > 0:
            return max_time_span * (1 - infr / 100)
        else:
            return 0


if __name__ == "__main__":

    app = Application()
    app.execute_radar()
