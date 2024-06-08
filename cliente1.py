import grpc
import messenger_pb2
import messenger_pb2_grpc
import threading

def connect(server_address, client_name):
    channel = grpc.insecure_channel(server_address)
    stub = messenger_pb2_grpc.MessengerStub(channel)
    response = stub.Connect(messenger_pb2.ClientInfo(name=client_name))
    return response.connected, stub

def send_message(stub, sender, receiver, content):
    stub.SendMessage(messenger_pb2.Message(sender=sender, receiver=receiver, content=content))

def receive_messages(stub, client_name):
    for message in stub.ReceiveMessages(messenger_pb2.ClientInfo(name=client_name)):
        print(f"Mensagem recebida de {message.sender}: {message.content}")

def main():
    server_address = 'localhost:50051'
    client_name = input("Digite seu nome: ")

    connected, stub = connect(server_address, client_name)
    if connected:
        print(f"{client_name} conectado ao servidor!")
        threading.Thread(target=receive_messages, args=(stub, client_name)).start()
        while True:
            message = input("Digite uma mensagem para enviar (ou 'sair' para sair): ")
            if message.lower() == 'sair':
                break
            receiver = input("Digite o nome do destinatário da mensagem: ")
            send_message(stub, client_name, receiver, message)
    else:
        print("Falha ao conectar ao servidor.")

if __name__ == '__main__':
    main()
