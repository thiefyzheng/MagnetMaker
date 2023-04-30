import os
import json
import sys
import bencodepy
import hashlib
import base64
import time

# Define the path to the uploads directory
uploads_path = '/home/stablebay/uploads'

def make_magnet_from_file(torrent_file) :
    with open(torrent_file, 'rb') as f:
        metadata = bencodepy.decode(f.read())
        subj = metadata[b'info']
        hashcontents = bencodepy.encode(subj)
        digest = hashlib.sha1(hashcontents).digest()
        b32hash = base64.b32encode(digest).decode()
        magnet_link = 'magnet:?' \
                      + 'xt=urn:btih:' + b32hash \
                      + '&dn=' + metadata[b'info'][b'name'].decode() \
                      + '&tr=' + metadata[b'announce'].decode() \
                      + '&xl=' + str(metadata[b'info'][b'length'])
        return magnet_link

# Run the loop every 1 second
while True:
    # Iterate through all subdirectories in uploads directory
    for model_name in os.listdir(uploads_path):
        model_dir = os.path.join(uploads_path, model_name)
        if not os.path.isdir(model_dir):
            continue

        # Check if model has a torrent file
        torrent_file = None
        for file_name in os.listdir(model_dir):
            if file_name.endswith('.torrent'):
                torrent_file = os.path.join(model_dir, file_name)
                break
        if not torrent_file:
            continue

        # Load model info from JSON file
        json_path = os.path.join(model_dir, 'info.json')
        with open(json_path, 'r') as f:
            model_info = json.load(f)

        # Extract magnet link from torrent file
        magnet_link = make_magnet_from_file(torrent_file)

        # Update model info with magnet link and save to JSON file
        model_info['magnet_link'] = magnet_link
        with open(json_path, 'w') as f:
            json.dump(model_info, f)

    # Wait for 1 second before running the loop again
    time.sleep(1)
