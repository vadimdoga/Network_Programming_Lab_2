# Network_Programming_Lab_2

## Getting Started

## Portocol Side

Implement own protocol based on UDP.

### Mandatory Tasks

```
1. Implement a protocol atop UDP
- With a method to make it more reliable, using either (1) error checking + retransmission (this is simple) or (2) error correction (a bit harder but cooler)
- Make the connection secure, using either symmetric streaming or asymmetric encryption

2. Then, once your protocol is more reliable and secure, make an application-level protocol on top of it, like FTP, or HTTP:
- A set of methods/verbs and rules on how to interact with it
- Model the protocol as a state machine, for documentation

```

## UML State Machine
![photo_2019-12-10_09-05-21](https://user-images.githubusercontent.com/43139007/70603328-f8eac500-1bfe-11ea-930c-47b5f7186599.jpg)

## Application Side

Implement application based on created protocol.

### Mandatory Tasks
```
3.To prove that everything is working as intended, make a server and a client using this nice protocol of yours.
```
### Description

Application: Chat in command line with multiple connections.
Commands?

* **connect** - for connection to server
* **send** - for sending to a specific connected PORT(client)
* **broadcast** - for sending to all connected PORTS(clients)
* **clients** - to see all connected PORTS(clients)
* **stop** - to disconnect from server
* **stop server** - to stop the server

### How to RUN?
```
python3 server_application.py BUFFER_SIZE PORT MAX_NR_OF_ClIENTS
python3 client_application.py BUFFER_SIZE PORT
```
## Built With

* [Python](https://www.python.org/)


## Authors

* **Doga Vadim** - *All work* - [vadimdoga](https://github.com/vadimdoga)
