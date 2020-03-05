#include "client.h"

#include <QDebug>

Client::Client(QObject *parent) : QObject(parent)
{
    ;
}

Client::~Client()
{
    for(int i=0; i<messengers.size(); i++)
    {
        messengers.at(i)->close();
        delete messengers.at(i);
    }
}

void Client::send(QMap<QString, QString> &the_header, const QByteArray &data, QString aim_ip, int aim_port)
{
    if(aim_ip!="" && aim_port!=0)
    {
        for(int i=0; i<messengers.length(); i++)
        {
            if(messengers.at(i)->IP==aim_ip && messengers.at(i)->port==aim_port)
            {
                messengers.at(i)->send(the_header, data);
                break;
            }
        }
    }
    else
    {
        for(int i=0; i<messengers.length(); i++)
        {
            messengers.at(i)->send(the_header, data);
        }
    }
}

void Client::add_connection(QString IP, int port)
{
    QTcpSocket *client = new QTcpSocket;
    Messenger *messenger = new Messenger(client, IP, port);
    connect(messenger, &Messenger::connect_success, this, &Client::connect_success_callback);
    connect(messenger, &Messenger::recv_message, this, &Client::receive_callback);
    connect(messenger, &Messenger::connect_fail, this, &Client::connect_fail_callback);
    connect(messenger, &Messenger::connect_close, this, &Client::client_close_callback);
    messengers.append(messenger);
    client->connectToHost(IP, port);

}

void Client::connect_fail_callback(Messenger *messenger)
{
    messenger->close();
    messengers.removeOne(messenger);
    qDebug() << "connect fail ->  " << messenger->IP << ":" << messenger->port;
}

void Client::connect_success_callback(Messenger *messenger)
{
    qDebug() << "success " << messenger->IP << ":" << messenger->port;
}

void Client::client_close_callback(Messenger *messenger)
{
//    messenger->close();
    messengers.removeOne(messenger);
    qDebug() << "connect close ->  " << messenger->IP << ":" << messenger->port;
}

void Client::receive_callback(Messenger *messenger)
{
    QMap<QString, QString> header;
    QMapIterator<QString, QString> i(messenger->header);
    while (i.hasNext()) {
        i.next();
        qDebug() << i.key() << ": " << i.value();
        if(i.key()!="CL") header.insert(i.key(), i.value());
    }

    messenger->send(header);
}

