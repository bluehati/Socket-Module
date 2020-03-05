#include "myclient.h"


void MyClient::connect_fail_callback(Messenger *messenger)
{
    messenger->close();
    messengers.removeOne(messenger);
    qDebug() << "myclient connect fail ->  " << messenger->IP << ":" << messenger->port;
}

void MyClient::connect_success_callback(Messenger *messenger)
{
    qDebug() << "myclient  success " << messenger->IP << ":" << messenger->port;
}

void MyClient::client_close_callback(Messenger *messenger)
{
//    messenger->close();
    messengers.removeOne(messenger);
    qDebug() << "myclient  connect close ->  " << messenger->IP << ":" << messenger->port;
}

void MyClient::receive_callback(Messenger *messenger)
{
    QMap<QString, QString> header;
    QMapIterator<QString, QString> i(messenger->header);
    while (i.hasNext()) {
        i.next();
        qDebug() << "my" << i.key() << ": " << i.value();
        if(i.key()!="CL") header.insert(i.key(), i.value());
    }

    messenger->send(header);
}
