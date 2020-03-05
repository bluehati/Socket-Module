#include "myserver.h"

void MyServer::receive_callback(Messenger *messenger)
{
    QMap<QString, QString> header;
    QMapIterator<QString, QString> i(messenger->header);
    while (i.hasNext()) {
        i.next();
        qDebug() << "myserver:" << i.key() << ": " << i.value();
        if(i.key()!="CL") header.insert(i.key(), i.value());
    }

    messenger->send(header);
}

void MyServer::new_connect_callback(Messenger *messenger)
{
    qDebug() << "myserver: get new connect " << messenger->IP << ":" << messenger->port;
}

void MyServer::client_close_callback(Messenger *messenger)
{
    messengers.removeOne(messenger);
    qDebug() << "myserver: connect close ->  " << messenger->IP << ":" << messenger->port;
}
