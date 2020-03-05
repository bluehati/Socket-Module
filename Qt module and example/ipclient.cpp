#include "ipclient.h"

void IPClient::set_info(QString my_ID, int my_port)
{
    ID = my_ID;
    port = my_port;
}

void IPClient::begin()
{
    if(!timer)
    {
        timer = new QTimer;
        connect(timer, &QTimer::timeout, this, &IPClient::report);
        timer->start(2000);
    }
}

void IPClient::stop()
{
    timer->stop();
    delete timer;
}


void IPClient::report()
{
    QMap<QString, QString> info;
    info.insert("ID", ID);
    info.insert("Port", QString::number(port));
    send(info);
}

void IPClient::connect_fail_callback(Messenger *messenger)
{
    messenger->close();
    messengers.removeOne(messenger);
    qDebug() << "connect fail ->  " << messenger->IP << ":" << messenger->port;
}

void IPClient::connect_success_callback(Messenger *messenger)
{
    qDebug() << "success " << messenger->IP << ":" << messenger->port;
}

void IPClient::client_close_callback(Messenger *messenger)
{
//    messenger->close();
    messengers.removeOne(messenger);
    qDebug() << "connect close ->  " << messenger->IP << ":" << messenger->port;
}

void IPClient::receive_callback(Messenger *messenger)
{
    if(messenger->header.contains("Broadcast"))
    {
        parser_devices(messenger->content);
    }
}

void IPClient::parser_devices(const QByteArray &data)
{
    online_devices.clear();
    QString my_ip = "";
    if(messengers.length()>0)
    {
        my_ip = messengers.at(0)->my_ip;
    }
    QString head = QString::fromUtf8(data);
    QStringList the_data = head.split(";");
    for(int i=0; i<the_data.length(); i++)
    {
        QStringList part = the_data.at(i).split(",");
        Device a = {part.at(0), part.at(1), part.at(2).toInt()};
        if(a.ID != ID && a.port != port && a.IP != my_ip)
        {
            online_devices.append(a);
        }

    }

    for(int i=0; i<online_devices.length(); i++)
    {
        qDebug() << online_devices.at(i).ID << ", " << online_devices.at(i).IP << ":" << online_devices.at(i).port;
    }
}
