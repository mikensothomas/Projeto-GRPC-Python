from concurrent import futures
import grpc
import messenger_pb2
import messenger_pb2_grpc
from queue import Queue

class MessengerServicer(messenger_pb2_grpc.MessengerServicer):
    def __init__(self):
        self.clients = {}
        self.categories = {
            "1": "aparelho eletrônico",
            "2": "veículo terrestre",
            "3": "animal"
        }
        self.player_categories = {}
        self.player_choices = {}
        self.message_queues = {}

    def Connect(self, request, context):
        client_name = request.name
        self.clients[client_name] = context
        self.message_queues[client_name] = Queue()
        print(f"Cliente {client_name} conectado.")
        return messenger_pb2.ConnectionStatus(connected=True)

    def ShowMenu(self, request, context):
        menu = "Escolha a categoria de palavras:\n"
        for key, category in self.categories.items():
            menu += f"{key}) {category}\n"
        return messenger_pb2.Menu(menu=menu)

    def ChooseCategory(self, request, context):
        client_name = request.name
        choice = request.choice
        if choice in self.categories:
            category = self.categories[choice]
            self.player_categories[client_name] = category
            print(f"Cliente {client_name} escolheu a categoria: {category}")
            for other_client in self.clients:
                if other_client != client_name:
                    self.message_queues[other_client].put(messenger_pb2.Message(
                        sender=client_name,
                        content=f"Categoria escolhida pelo outro jogador: {category}"
                    ))
        else:
            print(f"Escolha inválida.")
        return messenger_pb2.Empty()

    def ChooseItem(self, request, context):
        client_name = request.name
        item = request.item
        self.player_choices[client_name] = item
        print(f"Cliente {client_name} escolheu o item: {item}")
        for other_client in self.clients:
            if other_client != client_name:
                self.message_queues[other_client].put(messenger_pb2.Message(
                    sender=client_name,
                    content="O outro jogador escolheu um item. Você pode começar a fazer perguntas."
                ))
        return messenger_pb2.Empty()

    def SendMessage(self, request, context):
        receiver = request.receiver
        if receiver in self.clients:
            message = messenger_pb2.Message(sender=request.sender, receiver=receiver, content=request.content)
            self.message_queues[receiver].put(message)
            print(f"Mensagem enviada de {request.sender} para {receiver}")
            return messenger_pb2.Empty()
        else:
            print(f"Destinatário {receiver} não encontrado.")
            return messenger_pb2.Empty()

    def ReceiveMessages(self, request, context):
        client_name = request.name
        while True:
            if client_name in self.message_queues:
                message = self.message_queues[client_name].get()
                yield message

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    messenger_pb2_grpc.add_MessengerServicer_to_server(MessengerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Servidor conectado na porta 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
