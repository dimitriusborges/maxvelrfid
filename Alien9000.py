import telnetlib

HOST = "127.0.0.1"
PORT = "20000"
LOGIN = "alien"
PASSWORD = "password"
read = "t"


class Alien9000:

    def __init__(self):
        """"""
        self.tn = None

    def open_con(self, ip=HOST, porta=PORT):
        self.tn = telnetlib.Telnet()
        self.tn.open(ip, porta)

    def close_con(self):
        self.tn.close()

    def login(self, user=LOGIN, password = PASSWORD):

        self.tn.write(user.encode('ascii') + b"\n")

        self.tn.read_until(b'\r\n\r\nPassword>')

        self.tn.write(password.encode('ascii') + b"\n")

        self.tn.read_until(b'\r\n\r\nAlien >')

    def tag_read(self):

        tags_list = []
        ants_list = []
        self.tn.write(b"t\n")

        result = self.tn.read_until(b'\r\n\r\nAlien >')

        result = str(result)
        result = result.split(',')

        for string in result:
            if "Tag:" in string:
                tags_list.append(string)
            if "Ant" in string:
                ants_list.append(string)

        limit = len(tags_list)
        for tags in range(limit):
            start = tags_list[tags].index("Tag:")
            tags_list.append((tags_list[tags])[start + len("Tag:"):])

        for tags in range(limit):
            tags_list.pop(0)

        limit = len(ants_list)
        for ants in range(limit):
            start = ants_list[ants].index("Ant:")
            ants_list.append((ants_list[ants])[start + len("Ant:"):])

        for ants in range(limit):
            ants_list.pop(0)

        return tags_list, ants_list


if __name__ == "__main__":

    a9 = Alien9000()

    a9.open_con()
    a9.login()
    print(a9.tag_read())
    a9.close_con()
