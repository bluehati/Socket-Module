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
client的这种设计有问题？ 为什么没有及时触发接收事件, 好像就是因为WRITE事件，去掉就好了
"""

"""
2020.2.4  重新思考发现了巨量的问题
1、客户端之前都是从单一链接的角度设计的，应该重新替换成大量链接的设计视角，于是需要添
加一系列的新功能，广播，客户端关闭等等
2、客户端之前忘记做连接失败的检测了，我新增了一个使用Timer的检测方案，然后才
发现select竟然会自动检测，如果连接失败会直接返回读事件，同时会出现ConnectionRefusedError错误
我还是留下了检测方案，说不定有用
3、要新增一个send函数，负责完成消息发送，并且自动处理发送错误问题
4、客户端和服务端的结构会越来越相似
"""

__all__ = ["Client"]

class Client :

    def __init__(self, catch_break=True) :

        self.__selector = selectors.DefaultSelector()

        self.messengers = []

        self._lock = threading.Lock()

        if catch_break:
            signal.signal(signal.SIGINT, self.__interrupt_handler)


    def connect_fail_callback(self, client) :
        """
        连接失败
        """
        pass

    def connect_success_callback(self, client) :
        """
        连接成功
        """
        pass

    def client_close_callback(self, client, alive_client_num) :
        """
        客户端关闭
        """
        pass

    def receive_callback(self, client): 
        """
        收到信息
        """
        print(client.addr, "recv:", client.header, client.content)

    
    def add_connection(self, ip, port) :
        """
        连接到一个服务器
        """
        socket = self.__generate_client((ip, port))

        client = lib.Messenger(self.__selector, socket, (ip, port))

        t = threading.Timer(5, self.__connect_check, args=(client, ))
        t.start()

        self.__selector.register(socket, selectors.EVENT_READ, data=client)

        self._lock.acquire()
        self.messengers.append(client)
        self._lock.release()

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

    def stop(self): 
        self.__interrupt_handler(0, 0)


    def __connect_check(self, client) :
        """
        检测连接是否成功
        """
        if not self.send(client, {"TP": "Check"}): 
            if client.connect_status==0: 
                self.connect_fail_callback(client)
                client.connect_status = 1
        else: 
            if client.connect_status==0:
                self.connect_success_callback(client)
                client.connect_status = 2

    def __interrupt_handler(self, sig, frame): 
        """
        捕捉到ctr-c
        定义处理方式为关闭所有socket
        private
        """
        for client in self.messengers: 
            self.__selector.unregister(client.socket)
            client.socket.close()

        print("bye~~~")
        sys.exit(0)

    def __generate_client(self, addr) :
        """
        生成，配置一个TCP客户端
        private
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(addr)

        return sock 

    def _listen(self) :
        """
        持续监听
        外部可以调用
        不要override
        """
        while True: 
            events = self.__selector.select(timeout=1)

            for key, mask in events:
                client = key.data
                try :
                    client.process_read()
                except lib.PartnerCloseError:
                    self._close_client(client)
                except lib.RecvNothing:
                    self._close_client(client)
                except lib.ConnectRefuse: 
                    self._close_client(client)
                    if client.connect_status==0: 
                        self.connect_fail_callback(client)
                        client.connect_status = 1

                else:
                    if client.connect_status==0: 
                        self.connect_success_callback(client)
                        client.connect_status = 2
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
        except KeyError: 
            pass
        if need_lock:
            self._lock.acquire()
            if client in self.messengers: 
                self.messengers.remove(client)
            self._lock.release()
        else: 
            if client in self.messengers: 
                self.messengers.remove(client)

        # print("close one client:", len(self.messengers))
        self.client_close_callback(client, len(self.messengers))


    def _run(self): 
        """
        示范性自定义方法
        """
        listen_thread = threading.Thread(target=self._listen, daemon=True)

        listen_thread.start()

        while True: 
            pass

if __name__ == '__main__':
    
    client = Client()
    client.add_connection("127.0.0.1", 63336)
    client.add_connection("127.0.0.1", 63335)
    client._run()