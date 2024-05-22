from concurrent import futures
import grpc
import messenger_pb2
import messenger_pb2_grpc

class MessengerServicer(messenger_pb2_grpc.MessengerServicer):
    def __init__(self):
        self.clients = {}
        self.client_stream = {}

    def Connect(self, request, context):
        client_name = request.name
        self.clients[client_name] = context
        self.client_stream[client_name] = context
        print(f"Cliente {client_name} conectado.")
        if len(self.clients) == 2:
            return messenger_pb2.ConnectionStatus(connected=True)
        else:
            return messenger_pb2.ConnectionStatus(connected=False)

    def SendMessage(self, request, context):
        receiver = request.receiver
        if receiver in self.clients:
            self.clients[receiver].send_message(request)
            return messenger_pb2.Empty()
        else:
            return messenger_pb2.Empty()

    def ReceiveMessage(self, request, context):
        client_name = request.name
        for message in self.client_stream[client_name].incoming_messages():
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
