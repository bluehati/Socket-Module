from server import Server
import time
import threading

class IPServer(Server):

    def __init__(self, ip, port, alive_time=3000, catch_break=True): 
        Server.__init__(self, ip, port ,catch_break)
        self.online_device = {} 
        self.server_book = {}

        self.max_alive_time = alive_time

    def new_connect_callback(self, client): 
        print("get new connect", client.addr)

    def client_close_callback(self, client, alive_client_num) :
        """
        客户端关闭
        """
        try:
            self.online_device.pop(client.id)
        except:
            pass
        print("client close", client.addr, alive_client_num)

    def receive_callback(self, client): 
        """
        子类通过重写这个方法实现对于接收到客户端信息之后的处理
        """
        # print("recv")
        # print(client.header)
        if "ID" in client.header :
            if client.id in self.online_device: 
                self.online_device[client.id]["time"] = time.time()
                self.online_device[client.id]["ID"] = client.header["ID"]
                self.online_device[client.id]["Port"] = client.header["Port"]
            else: 
                self.online_device[client.id] = {"Port": client.header["Port"], "time":time.time(), "ID":client.header["ID"], "messenger":client}



    def broadcast_work(self): 
        while True: 
            clients = []
            message = ""
            now = time.time()
            # print(now, self.online_device)
            for key in self.online_device: 
                client = self.online_device[key]
                if now-client["time"]<=self.max_alive_time: 
                    clients.append(client["messenger"])
                    message += client["ID"]+","+client["messenger"].addr[0]+","+client["Port"]+";"

            message = message.rstrip(";")

            self.multicast(clients, {"Broadcast":""}, message.encode("utf-8"))

            time.sleep(2)

    def run(self):
        listen_thread = threading.Thread(target=self._listen, daemon=True)
        broadcast_thread = threading.Thread(target=self.broadcast_work, daemon=True)

        listen_thread.start()
        broadcast_thread.start()

        while True:
            pass


if __name__ == '__main__':
    
    s = IPServer("0.0.0.0", 5000)
    s.run()














