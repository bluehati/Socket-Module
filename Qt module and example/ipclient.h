#ifndef IPCLIENT_H
#define IPCLIENT_H

#include <QObject>
#include <QTimer>

#include "client.h"
#include "datatype.h"

class IPClient : public Client
{
public:
    void set_info(QString my_ID, int my_port);
    void begin();
    void stop();

    QList<Device> online_devices;

public slots:
    void connect_fail_callback(Messenger *messenger);
    void connect_success_callback(Messenger *messenger);
    void client_close_callback(Messenger *messenger);
    void receive_callback(Messenger *messenger);

private:
    QTimer *timer = nullptr;
    QString ID;
    int port;

    void report();
    void parser_devices(const QByteArray &data);
};

#endif // IPCLIENT_H
