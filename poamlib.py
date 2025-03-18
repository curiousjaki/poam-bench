import grpc
import base64
import json
import poam_pb2
import poam_pb2_grpc
from time import sleep
from timeit import default_timer as timer
from contextlib import contextmanager
server_address = "localhost:50051"

max_len = 1024*1024*16-10
options = [
    ('grpc.max_receive_message_length', max_len),  # Set to 50MB
    ('grpc.max_send_message_length', max_len),
    ('grpc.max_message_length', max_len),
    ('grpc.max_metadata_size', max_len),
]

proving_image_id =  [
            2948630792,
            2482136711,
            1512618692,
            3197082418,
            820963868,
            463243005,
            2815130045,
            3835354657
            ]

@contextmanager
def experiment_timer():
    start = timer()
    elapser = lambda: timer() - start
    yield lambda: elapser()
    end = timer()
    elapser = lambda: end-start

def proof_request(method_payload, input_data: json = None, chained = False, proving_image_id = proving_image_id, server_address = "localhost:50051") -> tuple[dict, int]:
    # Load input data from JSON file

    # Create a channel and a stub
    channel = grpc.insecure_channel(server_address, options=options)
    stub = poam_pb2_grpc.VerifiableProcessingServiceStub(channel)
    
    if not chained:
        # Construct the ProveRequest message using data from JSON
        request = poam_pb2.ProveRequest(
            poam_metadata=poam_pb2.PoamMetadata(
                current_image_id=proving_image_id,
            ),
            method_payload=method_payload
        )
    else:
        if input_data is None:
            raise ValueError("Input file must be provided for chained proof requests")
        request = poam_pb2.ProveRequest(
            poam_metadata=poam_pb2.PoamMetadata(
                previous_proof  = poam_pb2.Proof(
                    image_id = input_data["proof"]["imageId"],
                    receipt = base64.b64decode(input_data["proof"]["receipt"].encode("utf-8"))
                ),
                current_image_id=input_data["proof"]["imageId"]
            ),
            method_payload=method_payload
        )
    # Call the prove method
    try:
        response = stub.prove(request)
        # Convert response to a dictionary
        
        image_id = response.proof_response.image_id
        receipt = base64.b64encode(response.proof_response.receipt)
        #print(receipt)

        receipt_size = len(response.proof_response.receipt)
        #
        response_dict = {
            "verificationValue": float(response.public_output),
            "proof":{
                "imageId": list(image_id),
                "receipt": receipt.decode("utf-8")
            }
        }
        return response_dict, receipt_size
    except grpc.RpcError as e:
        breakpoint()
        print("gRPC error:", e.details())


def compose_request(proof_chain, server_address = "localhost:50051")->tuple[dict, int]:
    # Create a channel and a stub
    channel = grpc.insecure_channel(server_address, options=options)
    stub = poam_pb2_grpc.VerifiableProcessingServiceStub(channel)

    # Construct the ProveRequest message using data from JSON
    request = poam_pb2.CompositionRequest(
        proof_chain = proof_chain,
    )
    
    try:
        response = stub.compose(request)
        # Convert response to a dictionary
        image_id = response.proof_response.image_id
        receipt_size = len(response.proof_response.receipt)
        receipt = base64.b64encode(response.proof_response.receipt)
        #
        response_dict = {
            "verificationValue": 0.0,
            "proof":{
                "imageId": list(image_id),
                "receipt": receipt.decode("utf-8")
            }
        }
        return response_dict, receipt_size
    except grpc.RpcError as e:
        print("gRPC error:", e.details())

def verify_request(proof, verification_value = 0.0, server_address = "localhost:50051")->tuple:
    # Create a channel and a stub
    channel = grpc.insecure_channel(server_address, options=options)
    stub = poam_pb2_grpc.VerifiableProcessingServiceStub(channel)
    # Construct the ProveRequest message using data from JSON
    request = poam_pb2.VerifyRequest(
        verification_value = verification_value,
        proof = proof
    )
    #poam_pb2.Proof(image_id=input_data1["proof"]["imageId"], receipt=base64.b64decode(input_data1["proof"]["receipt"].encode("utf-8")))
    # Call the prove method
    try:
        response = stub.verify(request)
        # Convert response to a dictionary
        #print(response.is_valid_executed)
        #print(response.public_output)
        return (response.is_valid_executed, response.public_output)
        # Write response to a JSON file
    except grpc.RpcError as e:
        print("gRPC error:", e.details())

def combined_request(input_data: json, server_address = "localhost:50051")->tuple[dict,int]:
    channel = grpc.insecure_channel(server_address, options=options)
    stub = poam_pb2_grpc.VerifiableProcessingServiceStub(channel)
    # Construct the ProveRequest message using data from JSON
    request = poam_pb2.CombinedRequest(
        method_payload = input_data
    )
    
    try:
        response = stub.combined(request)
        # Convert response to a dictionary
        image_id = response.proof_response.image_id
        receipt_size = len(response.proof_response.receipt)
        receipt = base64.b64encode(response.proof_response.receipt)
        #
        response_dict = {
            "verificationValue": float(response.public_output),
            "proof":{
                "imageId": list(image_id),
                "receipt": receipt.decode("utf-8")
            }
        }
        return response_dict, receipt_size
    except grpc.RpcError as e:
        print("gRPC error:", e.details())