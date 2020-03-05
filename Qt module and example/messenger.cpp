#include "messenger.h"
#include <QStringList>


Messenger::Messenger(QTcpSocket *client, QString the_ip, int the_port, QObject *parent) : QObject(parent)
{
    socket = client;
    my_ip = client->localAddress().toString();
    connect(socket, &QTcpSocket::connected, this, &Messenger::connect_done);
    connect(socket, &QTcpSocket::readyRead, this, &Messenger::read);
    connect(socket, QOverload<QAbstractSocket::SocketError>::of(&QAbstractSocket::error), this, &Messenger::socket_error);
    IP = the_ip;
    port = the_port;

}

void Messenger::send(QMap<QString, QString> &the_header, const QByteArray &data)
{
    if(data.length()>0)
    {
        the_header.insert("CL", QString::number(data.length()));
    }
    else
    {
        the_header.insert("CL", "0");
    }

    QString head = "";
    QMapIterator<QString, QString> i(the_header);
    while (i.hasNext()) {
        i.next();
        head += i.key() + ": " + i.value() + ";";
    }
    head = head.left(head.length()-1);
    QByteArray head_byte = head.toUtf8();
    int length = head_byte.length();
    QByteArray head_1 = Int2Byte(length);

    head_1 = head_1 + head_byte;
    if(data.length()>0) head_1 = head_1 + data;

    write_data(head_1);
}

void Messenger::close()
{
    socket->close();
    socket->abort();
    delete socket;
}

void Messenger::read()
{
    QByteArray data;
    read_data(2, data);
    int header_length = Byte2Int(data);
    data = data.right(data.length()-2);

    read_data(header_length, data);
    QString header_string = QString::fromUtf8(data.left(header_length));
    parse_header(header_string);
    data = data.right(data.length()-header_length);
    int content_length = header["CL"].toInt();
    content.clear();

    if(content_length>0)
    {
        read_data(content_length, content);
    }
    if(header.contains("TP") && header["TP"]=="Check")
    {
        ;
    }
    else {
        emit recv_message(this);
    }

}


void Messenger::read_data(int length, QByteArray &data)
{
    while(data.length()<length)
    {
        data.append(socket->read(length));
    }
}

void Messenger::write_data(QByteArray &data)
{
    while(data.length()>0)
    {
        int len = socket->write(data);
        data = data.right(data.length()-len);
    }

}


int Messenger::Byte2Int(const QByteArray &data)
{
    uint16_t res = (((uint16_t) data[1])<<8) + ((uint16_t) data[0]);
    return ((int) res);
}

QByteArray Messenger::Int2Byte(const int &length)
{
    uint16_t s = (uint16_t) length;
    QByteArray data;
    data.resize(2);
    data[0] = (s & 255);
    data[1] = (s >> 8);
    return data;
}

void Messenger::parse_header(QString &header_string)
{
    header.clear();
    QStringList data = header_string.split(";");
    for(int i=0; i<data.length(); i++)
    {
        QStringList part = data.at(i).split(":");
        header.insert(part.at(0), part.at(1));
    }

}

void Messenger::connect_done()
{
    emit connect_success(this);
}

void Messenger::socket_error(QAbstractSocket::SocketError error)
{
    switch (error) {
    case QAbstractSocket::ConnectionRefusedError :
        emit connect_fail(this);
        break;
    case QAbstractSocket::RemoteHostClosedError :
        emit connect_close(this);
        break;
    case QAbstractSocket::SocketAccessError :
        emit connect_close(this);
        break;
    case QAbstractSocket::SocketTimeoutError :
        emit connect_fail(this);
        break;

    default:
        qDebug() << error;
    }
}
