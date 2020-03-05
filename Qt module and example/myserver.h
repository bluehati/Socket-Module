#ifndef MYSERVER_H
#define MYSERVER_H

#include <QObject>
#include "server.h"

class MyServer : public Server
{
public slots:

    void new_connect_callback(Messenger *messenger);
    void client_close_callback(Messenger *messenger);
    void receive_callback(Messenger *messenger);
};

#endif // MYSERVER_H
