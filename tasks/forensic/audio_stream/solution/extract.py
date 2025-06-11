import json
from tqdm import tqdm

def get_contents(packets):
    result = b""
    for packet in tqdm(packets):
        try:
            flags = packet['_source']['layers']['tcp']['tcp.flags']
            if flags != "0x0018":
                continue
            packet_data = bytes.fromhex(packet['_source']['layers']['tcp']['tcp.payload'].replace(":", ""))
            if packet_data == b"OK":
                continue
            if packet_data == b"EOF":
                break
        except Exception as e:
            continue

        result += packet_data

    return result

with open('./capture.json', 'r') as f:
    packets_data = json.load(f)

result = get_contents(packets_data)

with open('./result.mp3', 'wb+') as f:
    f.write(result)
