import poamlib
import pandas as pd
import json
from tqdm import tqdm
import poam_pb2
import base64

def final_step_footprinting(df: pd.DataFrame, input_data: json) -> pd.DataFrame:
    df1 = pd.DataFrame(columns=["result", "proof_size", "seconds", "response"])
    method_payload = {}
    for i in tqdm(range(0, len(df.index))):
        method_payload[df.index[i]] = input_data[df.index[i]]
        with poamlib.experiment_timer() as elapsed:
            response, proof_size = poamlib.combined_request(json.dumps(method_payload))
            result = response["verificationValue"]
            time = elapsed()
            df1 = pd.concat([df1, pd.DataFrame({df.index[i]:{ "result": result, "proof_size": proof_size, "seconds": time, "response": response}}).T])
            #print(f"Experiment {i} took {time} seconds and yeilded a result of {result} with a proof size of {proof_size}")
    return pd.concat([df.copy(), df1], axis=1)

def activity_footprinting_unchained(df: pd.DataFrame, input_data: json)-> pd.DataFrame: 
    df1 = pd.DataFrame(columns=["result", "proof_size", "seconds", "response"])
    for i in tqdm(range(0, len(df.index))):
        method_payload = json.dumps({
            "a": df.loc[df.index[i]]["a"],
            "b": df.loc[df.index[i]]["b"],
            "operation":df.loc[df.index[i]]["operation"]
            })
        with poamlib.experiment_timer() as elapsed:
            response, proof_size = poamlib.proof_request(method_payload)
            result = response["verificationValue"]
            time = elapsed()
            df1 = pd.concat([df1, pd.DataFrame({df.index[i]:{ "result": result, "proof_size": proof_size, "seconds": time, "response": response}}).T])
            #print(f"Experiment {i} took {time} seconds and yeilded a result of {result} with a proof size of {proof_size}")
    return pd.concat([df.copy(), df1], axis=1)

def composition_footprinting_unchained(df_clean:pd.DataFrame, df: pd.DataFrame)->pd.DataFrame:
    df1 = pd.DataFrame(columns=["result", "proof_size", "seconds", "response"])
    proof_chain = []
    for i in tqdm(range(0, len(df.index))):
        input_data = df.loc[df.index[i]]["response"]
        proof_chain.append(poam_pb2.Proof(
                    image_id = input_data["proof"]["imageId"],
                    receipt = base64.b64decode(input_data["proof"]["receipt"].encode("utf-8"))
                ))
        with poamlib.experiment_timer() as elapsed:
            response, proof_size = poamlib.compose_request(proof_chain)
            result = response["verificationValue"]
            time = elapsed()
            df1 = pd.concat([df1, pd.DataFrame({df.index[i]:{ "result": result, "proof_size": proof_size, "seconds": time, "response": response}}).T])
            #print(f"Experiment {i} took {time} seconds and yeilded a result of {result} with a proof size of {proof_size}")
    return pd.concat([df_clean.copy(), df1], axis=1)

def activity_footprinting_chained(df: pd.DataFrame, input_data: json)-> pd.DataFrame:   
    df1 = pd.DataFrame(columns=["result", "proof_size", "seconds", "response"])
    previous = None
    chained = False
    for i in tqdm(range(0, len(df.index))):
        method_payload = json.dumps({
            "a": df.loc[df.index[i]]["a"],
            "b": df.loc[df.index[i]]["b"],
            "operation":df.loc[df.index[i]]["operation"]
            })
        if i > 0:
            previous = df1.loc[df.index[i-1]]["response"]
            chained = True
        with poamlib.experiment_timer() as elapsed:
            response, proof_size = poamlib.proof_request(method_payload, previous, chained)
            result = response["verificationValue"]
            time = elapsed()
            df1 = pd.concat([df1, pd.DataFrame({df.index[i]:{ "result": result, "proof_size": proof_size, "seconds": time, "response": response}}).T])
            #print(f"Experiment {i} took {time} seconds and yeilded a result of {result} with a proof size of {proof_size}")
    return pd.concat([df.copy(), df1], axis=1)

def proof_verification(df: pd.DataFrame)-> pd.DataFrame:
    df1 = pd.DataFrame(columns=["verified_value", "valid", "verification_seconds"])
    for i in tqdm(range(0, len(df.index))):
        response = df.loc[df.index[i]]["response"]
        proof = poam_pb2.Proof(
                image_id = response["proof"]["imageId"],
                receipt = base64.b64decode(response["proof"]["receipt"].encode("utf-8"))
            )
        with poamlib.experiment_timer() as elapsed:
            valid, result = poamlib.verify_request(proof)
            time = elapsed()
            df1 = pd.concat([df1, pd.DataFrame({df.index[i]:{ "verified_value": result, "valid": valid, "verification_seconds": time}}).T])
        
            #print(f"Experiment {i} took {time} seconds and yeilded a result of {result} with a proof size of {proof_size}")
    return pd.concat([df.copy(), df1], axis=1)