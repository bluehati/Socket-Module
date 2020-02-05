from client import Client
import threading

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


    def do_something(self): 
        while True:
            a = input("choose operation: (0, add connect;  1, send message; 2, broadcast)\n")
            if int(a)==0 :
                b = input("give me ip and port like this ip:port\n")
                s = b.split(":")
                print(s)
                self.add_connection(s[0], int(s[1]))
            elif int(a)==1 :
                for index, client in enumerate(self.messengers): 
                    print(index, client.addr)
                b = input("choose aim: ")
                client = self.messengers[int(b)]
                message = input("give me message >> ")
                print(message)
                self.send(client, {"info":message})
            elif int(a)==2 :
                print("aim: ")
                for index, client in enumerate(self.messengers): 
                    print(index, client.addr)
                b = input("give me message >> ")
                print(b)
                self.broadcast({"info":b})

    def run(self): 
        listen_thread = threading.Thread(target=self._listen, daemon=True)
        t_thread = threading.Thread(target=self.do_something, daemon=True)

        listen_thread.start()
        t_thread.start()

        while True: 
            pass



if __name__ == '__main__':
    
    c = SClient()
    c.run()










