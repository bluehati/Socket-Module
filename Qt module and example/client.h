#ifndef CLIENT_H
#define CLIENT_H

#include "messenger.h"

#include <QObject>
#include <QTcpSocket>
#include <QString>
#include <QList>

class Client : public QObject
{
    Q_OBJECT
public:
    explicit Client(QObject *parent = nullptr);
    ~Client();

    void send(QMap<QString, QString> &the_header, const QByteArray &data=NULL, QString aim_ip="", int aim_port=0);

    QList<Messenger *> messengers;
    void add_connection(QString IP, int port);

public slots:

    virtual void connect_fail_callback(Messenger *messenger);
    virtual void connect_success_callback(Messenger *messenger);
    virtual void client_close_callback(Messenger *messenger);
    virtual void receive_callback(Messenger *messenger);

signals:


private:


};

#endif // CLIENT_H
