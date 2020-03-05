#ifndef MYCLIENT_H
#define MYCLIENT_H

#include "client.h"
#include "messenger.h"

class MyClient : public Client
{
public slots:
    void connect_fail_callback(Messenger *messenger);
    void connect_success_callback(Messenger *messenger);
    void client_close_callback(Messenger *messenger);
    void receive_callback(Messenger *messenger);
};

#endif // MYCLIENT_H
