import socket
import struct
import json 
import csv
import time

import cv2
import numpy as np

HOST = "0.0.0.0"
PORT = 5000

def recv_exact(sock, n):
    """Receive exactly n bytes, returns None at connection loss"""
    chunks = []
    remaining = n
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)

    return b"".join(chunks) #perform a join on the byte array.

def receive_packet(sock):
    """Expects JSON header as a 4 byte unsigned big-endian, returns metadata and image in byteform"""
    length = recv_exact(sock, 4)
    if length is None:
        return None, None
    #"! signifies network/big endian data type, I is for unsigned int"
    header_length = struct.unpack("!I", length)[0]

    if not 0 < header_length <= 1024 * 1024:
        raise ValueError("Invalid Header Length")

    header = recv_exact(sock, header_length)
    if header is None:
        return None, None
    metadata = json.loads(header.decode("utf-8"))
    image_size = int(metadata["image_bytes"])

    if not 0 < image_size < 12 * 1920 * 1080: #Semi-arbitrary decision of 12 bytes per pixel for a full hd image. The quest supports up to full hd streaming.
        raise ValueError("Invalid Image Size!")
    
    image_bytes = recv_exact(sock, image_size)
    if image_bytes is None:
        return None, None

    return metadata, image_bytes

def main(): 
    #specifying IPv4 protocol, SOCK_STREAM for tcp socket, SOC_DGRAM for UDP socket (might opt into it later)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        #Documentation hell for these, but 
        #"The level argument specifies the protocol level at which the option resides. To retrieve options at the socket level, specify the level argument as SOL_SOCKET."
        # -UNIX documentation
        #REUSEADDR for reuse of local address. 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(1)

        print(f"Waiting for Meta Quest 3 on port {PORT}..")

        conn, addr = server.accept()

        with conn:
            print("Connected:", addr)
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

            with open("quest_poses.csv", "w", newline="") as f:
                writer = csv.DictWriter(f, 
                                        fieldnames = [
                                            "receipt_timestamp",
                                            "sequence",
                                            "camera_timestamp",
                                            "camera_position",
                                            "camera_position",
                                            "camera_rotation_quat", #xyzw should be quaternion rotation
                                            "head_position",
                                            "head_rotation_quat",
                                            "image_width",
                                            "image_height"
                                        ])
                writer.writeheader()

                try:
                    while True:
                        metadata, imagebytes = receive_packet(conn)
                        if metadata is None:
                            break

                        #decode the JPEG
                        encoded = np.frombuffer(imagebytes, dtype=np.uint8)
                        frame = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

                        if frame is None:
                            print("Failed to Read Image!!")
                            continue


                        #complex values such as matrices and vectors are going through json dumps, simple scalar/int/floats can be passed straight up
                        row = {
                            "receipt_timestamp": time.time(),
                            "sequence": metadata.get("sequence"),
                            "camera_timestamp": metadata.get("camera_timestamp"),
                            "camera_position": json.dumps(metadata.get("camera_position")),
                            "camera_rotation_quat": json.dumps(metadata.get("camera_rotation_quat")),
                            "head_position": json.dumps(metadata.get("head_position")),
                            "head_rotation_quat": json.dumps(metadata.get("head_rotation_quat")),
                            "image_width": metadata.get("image_width"),
                            "image_height": metadata.get("image_height"),
                        }

                        writer.writerow(row)
                        f.flush()

                        cv2.imshow("Quest camera", frame)

                        #Some keyboard control utility
                        #q to exit
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            break

                except (ConnectionError, OSError, ValueError, json.JSONDecodeError) as exception:
                    print("Receiver encountered a Error:", exception)

                finally:
                    cv2.destroyAllWindows()

        print("Connection Terminated.")

if __name__ == "__main__":
    main()
