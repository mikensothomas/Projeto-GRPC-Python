from concurrent import futures
import grpc
import messenger_pb2
import messenger_pb2_grpc
from queue import Queue

class MessengerServicer(messenger_pb2_grpc.MessengerServicer):
    def __init__(self):
        self.clients = {}
        self.message_queues = {}

    def Connect(self, request, context):
        client_name = request.name
        self.clients[client_name] = context
        self.message_queues[client_name] = Queue()
        print(f"Cliente {client_name} conectado.")
        return messenger_pb2.ConnectionStatus(connected=True)

    def SendMessage(self, request, context):
        receiver = request.receiver
        if receiver in self.message_queues:
            message = messenger_pb2.Message(sender=request.sender, receiver=request.receiver, content=request.content)
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
