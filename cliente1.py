import grpc
import messenger_pb2
import messenger_pb2_grpc

def connect(server_address, client_name):
    channel = grpc.insecure_channel(server_address)
    stub = messenger_pb2_grpc.MessengerStub(channel)
    response = stub.Connect(messenger_pb2.ClientInfo(name=client_name))
    return response.connected, stub

def main():
    server_address = 'localhost:50051'
    client_name = 'Cliente 1'

    connected, stub = connect(server_address, client_name)
    if connected:
        print("Conectado ao servidor!")
        while True:
            message = input("Digite uma mensagem para enviar (ou 'sair' para sair): ")
            if message.lower() == 'sair':
                break
            receiver = input("Digite o nome do destinatário da mensagem: ")
            stub.SendMessage(messenger_pb2.Message(sender=client_name, receiver=receiver, content=message))
    else:
        print("Falha ao conectar ao servidor.")

if __name__ == '__main__':
    main()
