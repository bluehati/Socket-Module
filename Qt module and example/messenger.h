#ifndef MESSENGER_H
#define MESSENGER_H

#include <QObject>
#include <QTcpSocket>
#include <QString>
#include <QByteArray>
#include <QMap>

#include <QAbstractSocket>
#include <QHostAddress>

class Messenger : public QObject
{
    Q_OBJECT
public:
    explicit Messenger(QTcpSocket *client, QString the_ip, int the_port, QObject *parent = nullptr);

    void close();

    void send(QMap<QString, QString> &the_header, const QByteArray &data=NULL);

    QString IP;
    int port;

    QString my_ip = "";

    QMap<QString, QString> header;
    QByteArray content;

signals:
    void recv_message(Messenger *messenger);
    void connect_success(Messenger *messenger);
    void connect_fail(Messenger *messenger);
    void connect_close(Messenger *messenger);


private:
    QTcpSocket *socket = nullptr;

    void read();

    void read_data(int length, QByteArray &data);

    void write_data(QByteArray &data);

    int Byte2Int(const QByteArray &data);

    QByteArray Int2Byte(const int &length);

    void parse_header(QString &header_string);

    void connect_done();

    void socket_error(QAbstractSocket::SocketError error);

};

#endif // MESSENGER_H
