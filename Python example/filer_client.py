from server import Server
from client import Client
import threading
import time

class SServer(Server):

    def new_connect_callback(self, client): 
        print("get new connect", client.addr)


    def client_close_callback(self, client, alive_client_num) :
        """
        客户端关闭
        """
        print("client close", client.addr, alive_client_num)

    def receive_callback(self, client): 
        """
        子类通过重写这个方法实现对于接收到客户端信息之后的处理
        """
        print("recv message:", client.header, client.content)



class SClient(Client):


    def connect_fail_callback(self, client) :
        """
        连接失败
        """
        print(client.addr, "----- connect fail")

    def connect_success_callback(self, client) :
        """
        连接成功
        """
        print(client.addr, "---- connect success")

    def client_close_callback(self, client, alive_client_num) :
        """
        客户端关闭
        """
        print(client.addr, "---- connect close,", alive_client_num)

    def receive_callback(self, client): 
        """
        收到信息
        """
        print(client.addr, "recv:", client.header, client.content)

    
class IPClient(Client): 

    def __init__(self, ID, ip, port, init_port): 
        Client.__init__(self)
        self.ID = ID
        self.add_connection(ip, port)
        self.Client = SClient(catch_break=False)

        self.Server = self.generate_server(init_port)

        self.address_book = []

        self.friends = {}

    def generate_server(self, init_port): 
        while True:
            try: 
                s = SServer("0.0.0.0", init_port, catch_break=False)
                return s
            except: 
                init_port += 1

    def connect_fail_callback(self, client) :
        """
        连接失败
        """
        print(client.addr, "----- connect fail")
        self.Server.stop()
        self.Client.stop()

    def connect_success_callback(self, client) :
        """
        连接成功
        """
        print("---- connect success")
        
        report_thread = threading.Thread(target=self.report, daemon=True)

        report_thread.start()


    def client_close_callback(self, client, alive_client_num) :
        """
        客户端关闭
        """
        print(client.addr, "---- connect close,", alive_client_num)

    def receive_callback(self, client): 
        """
        收到信息
        """
        if "Broadcast" in client.header :
            self.parse_broadcast(client.content)

    def parse_broadcast(self, message): 
        message = message.decode("utf-8")
        clients = message.split(";")
        record = [item.split(",") for item in clients]
        self.address_book = []

        for item in record:
            if item[0]==self.ID and (item[1]==self.Server.addr[0] or item[1]=="127.0.0.1") and int(item[2])==self.Server.addr[1] :
                pass
            else :
                self.address_book.append(item)

        print(self.address_book)
        

    def report(self): 

        while True: 
            self.broadcast({"ID":self.ID, "Port":self.Server.addr[1]})
            time.sleep(2)


    def choose(self):
        while True: 
            a = input("choose operation: (0, add connect;  1, send message; 2, broadcast)\n")
            if int(a)==0 :
                for index, client in enumerate(self.address_book): 
                    print(index, client)
                b = input("give me friend\n")
                self.Client.add_connection(self.address_book[int(b)][1], int(self.address_book[int(b)][2]))
            elif int(a)==1 :
                print("------- 0")
                for index, client in enumerate(self.Server.messengers): 
                    print(index, client.addr)
                print("------- 1")
                for index, client in enumerate(self.Client.messengers):
                    print(index, client.addr)
                b = input("choose aim: ")
                b = b.split(" ")
                b = [int(item) for item in b]
                message = input("give me message >> ")
                if b[0] == 0 :
                    self.Server.send(self.Server.messengers[b[1]], {"info":message})
                elif b[0] == 1 :
                    self.Client.send(self.Client.messengers[b[1]], {"info":message})

            elif int(a)==2 :
                print("aim: ")
                for index, client in enumerate(self.Server.messengers): 
                    print(index, client.addr)
                for index, client in enumerate(self.Client.messengers): 
                    print(index, client.addr)
                b = input("give me message >> ")
                print(b)
                self.Server.broadcast({"info":b})
                self.Client.broadcast({"info":b})


    def run(self): 
        ip_listen_thread = threading.Thread(target=self._listen, daemon=True)
        client_listen_thread = threading.Thread(target=self.Client._listen, daemon=True)
        server_listen_thread = threading.Thread(target=self.Server._listen, daemon=True)

        input_thread = threading.Thread(target=self.choose, daemon=True)

        ip_listen_thread.start()
        client_listen_thread.start()
        server_listen_thread.start()
        input_thread.start()

        while True: 
            pass



if __name__ == '__main__':
     
     s = IPClient("Stan", "127.0.0.1", 5000, 63330)
     s.run()






