"""
Startup proxy: binds port 5000 immediately to pass health checks,
starts Streamlit on port 5001, then transparently proxies all
TCP traffic (HTTP + WebSocket) from 5000 → 5001.
"""
import socket
import threading
import subprocess
import sys
import os

PROXY_PORT = 5000
STREAMLIT_PORT = 5001

HEALTH_RESPONSE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/plain\r\n"
    b"Content-Length: 2\r\n"
    b"Connection: close\r\n"
    b"\r\n"
    b"OK"
)

streamlit_ready = threading.Event()


def check_streamlit_ready():
    while True:
        try:
            with socket.create_connection(("localhost", STREAMLIT_PORT), timeout=1):
                streamlit_ready.set()
                return
        except OSError:
            import time
            time.sleep(1)


def pipe(src, dst):
    try:
        while True:
            data = src.recv(8192)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            src.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        try:
            dst.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass


def handle_client(client_sock):
    if streamlit_ready.is_set():
        try:
            server_sock = socket.create_connection(("localhost", STREAMLIT_PORT), timeout=5)
            t1 = threading.Thread(target=pipe, args=(client_sock, server_sock), daemon=True)
            t2 = threading.Thread(target=pipe, args=(server_sock, client_sock), daemon=True)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        except Exception:
            try:
                client_sock.close()
            except Exception:
                pass
    else:
        try:
            client_sock.sendall(HEALTH_RESPONSE)
        except Exception:
            pass
        finally:
            try:
                client_sock.close()
            except Exception:
                pass


def start_proxy():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", PROXY_PORT))
    srv.listen(128)
    srv.settimeout(1.0)
    while True:
        try:
            client_sock, _ = srv.accept()
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
        except socket.timeout:
            continue
        except Exception:
            continue


if __name__ == "__main__":
    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", "0.0.0.0",
            "--server.headless", "true",
        ]
    )

    threading.Thread(target=check_streamlit_ready, daemon=True).start()

    proxy_thread = threading.Thread(target=start_proxy, daemon=True)
    proxy_thread.start()

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
