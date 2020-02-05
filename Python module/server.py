"""
再次尝试重新设计Filer的服务器
author: stan
date: 2019.12.27 17:20
"""
import socket
import time
import sys
import selectors

import signal

import threading

import lib


"""
考虑加入日志功能  19.12.30 2：26

"""

"""
考虑加入多播功能 19.12.30 21:53
"""


class Server :

    def __init__(self, ip, port, catch_break=True) :

        self.addr = (ip, port)
        self.server = self.__generate_server()

        self.__selector = selectors.DefaultSelector()

        self.__selector.register(self.server, selectors.EVENT_READ, data=None)

        self.messengers = []

        self._lock = threading.Lock()

        if catch_break:
            signal.signal(signal.SIGINT, self.__interrupt_handler)

    def new_connect_callback(self, client): 
        pass


    def client_close_callback(self, client, alive_client_num) :
        """
        客户端关闭
        """
        pass

    def receive_callback(self, client): 
        """
        子类通过重写这个方法实现对于接收到客户端信息之后的处理
        """
        print("recv message:", client.header, client.content)

        client.send({"type":"message"}, client.content)

    def stop(self): 
        self.__interrupt_handler(0, 0)

    def __interrupt_handler(self, sig, frame): 
        """
        捕捉到ctr-c
        定义处理方式为关闭所有socket
        private
        """
        for client in self.messengers: 
            self.__selector.unregister(client.socket)
            client.socket.close()
        self.__selector.unregister(self.server)
        self.server.close()

        print("bye~~~")
        sys.exit(0)

    def __generate_server(self) :
        """
        生成TCP服务器
        配置TCP服务器
        private
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(self.addr)
        sock.listen()

        sock.setblocking(False)

        return sock


    def __accept(self, sock): 
        """
        接受一个客户端的连接
        private
        """
        client_sock, addr = sock.accept()
        client_sock.setblocking(False)

        client = lib.Messenger(self.__selector, client_sock, addr)

        self.__selector.register(client_sock, selectors.EVENT_READ, data=client)

        self._lock.acquire()
        self.messengers.append(client)
        self._lock.release()

        self.new_connect_callback(client)



    def _listen(self) :
        """
        持续监听
        供外部调用，但是不希望被override
        """
        while True: 
            events = self.__selector.select(timeout=None)

            for key, mask in events:
                # print(key.data) 
                if key.data == None: 
                    self.__accept(key.fileobj)
                else: 
                    client = key.data
                    try:
                        client.process_read()
                    except lib.PartnerCloseError:
                        self._close_client(client)
                    except lib.RecvNothing:
                        self._close_client(client)
                    else:
                        if "TP" in client.header and client.header["TP"]=="Check":
                            pass
                        else:
                            self.receive_callback(client)



    def _close_client(self, client, need_lock=True): 
        """
        关闭一个客户端，可以选择是否需要使用锁，注意
        绝对不可以遍历self.messengers同时删除

        外部可以调用
        不要override
        """
        try:
            self.__selector.unregister(client.socket)
        except:
            pass
        if need_lock:
            self._lock.acquire()
            if client in self.messengers: 
                self.messengers.remove(client)
            self._lock.release()
        else: 
            if client in self.messengers: 
                self.messengers.remove(client)

        self.client_close_callback(client, len(self.messengers))


    def send(self, client, header, content=None, close_when_fail=True, need_lock=True): 
        """
        向客户端发送信息
        need_lock: 关闭客户端是否需要锁
        close_when_fail: 发生错误是否关闭客户端

        --> Bool 发送成功与否
        """
        try: 
            client.send(header, content)
            return True
        except Exception as er: 
            if close_when_fail: 
                if need_lock: 
                    self._close_client(client)
                else:
                    self._close_client(client, need_lock=False)
        return False

    def broadcast(self, header, content=None): 
        """
        向全体连接广播信息
        """
        self._lock.acquire()
        remove_list = []
        for client in self.messengers: 
            if not self.send(client, header, content, need_lock=False, close_when_fail=False): 
                remove_list.append(client)
        for client in remove_list: 
            self._close_client(client, need_lock=False)
        self._lock.release()


    def multicast(self, clients, header, content=None): 
        """
        多播
        """
        self._lock.acquire()
        remove_list = []
        for client in clients: 
            if not self.send(client, header, content, need_lock=False, close_when_fail=False): 
                remove_list.append(client)
        for client in remove_list: 
            self._close_client(client, need_lock=False)
        self._lock.release()


    def _serve_forever(self): 
        """
        示范性自定义方法
        使用两个线程同时实现了listen和broadcast
        """
        run_thread = threading.Thread(target=self._listen, daemon=True)
        
        broadcast = threading.Thread(target=self._run_broadcast, daemon=True)


        run_thread.start()
        broadcast.start()

        while True :
            pass

    def _run_broadcast(self): 
        """
        示范性自定义方法
        配合serve_forever进行广播
        """
        while True: 
            print("broadcast")
            self.broadcast({"TP":"broadcast"}, "我是服务器".encode("utf-8"))
            time.sleep(2)




if __name__ == '__main__':
    
    server = Server("0.0.0.0", 63335)
    server._serve_forever()






