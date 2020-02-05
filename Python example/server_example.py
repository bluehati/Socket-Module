from server import Server
import threading


class SServer(Server) :

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

        # client.send({"type":"message"}, client.content)


    def do_something(self):
        while True:
            a = input("choose operation: (1, send message; 2, broadcast)\n")

            if int(a)==1 :
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

        while True :
            pass


if __name__ == '__main__':
    
    try: 
        se = SServer("0.0.0.0", 63335)
        se.run()
    except:
        print("generate fail")















