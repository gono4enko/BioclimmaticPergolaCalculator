"""
Startup proxy: binds port 5000 immediately to pass health checks,
starts Streamlit on port 5001, then transparently proxies all
TCP traffic (HTTP + WebSocket) from 5000 -> 5001.
"""
import socket
import threading
import subprocess
import sys
import os
import time

PROXY_PORT = 5000
STREAMLIT_PORT = 5001

HEALTH_RESPONSE = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: text/html; charset=utf-8\r\n"
    b"Connection: close\r\n"
    b"\r\n"
    b"<!DOCTYPE html><html><head>"
    b"<meta http-equiv='refresh' content='5'>"
    b"<style>body{display:flex;justify-content:center;align-items:center;"
    b"min-height:100vh;margin:0;background:#f0f2f6;font-family:sans-serif;}"
    b".loader{text-align:center;color:#004B9A;}"
    b".spinner{width:50px;height:50px;border:5px solid #e0e0e0;"
    b"border-top:5px solid #004B9A;border-radius:50%;"
    b"animation:spin 1s linear infinite;margin:0 auto 20px;}"
    b"@keyframes spin{to{transform:rotate(360deg)}}"
    b"</style></head><body><div class='loader'>"
    b"<div class='spinner'></div>"
    b"<h2>Loading...</h2>"
    b"<p>The application is starting, please wait</p>"
    b"</div></body></html>"
)

streamlit_ready = threading.Event()


def check_streamlit_ready():
    while True:
        try:
            with socket.create_connection(("127.0.0.1", STREAMLIT_PORT), timeout=1):
                streamlit_ready.set()
                print(f"[proxy] Streamlit is ready on port {STREAMLIT_PORT}", flush=True)
                return
        except OSError:
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
            server_sock = socket.create_connection(("127.0.0.1", STREAMLIT_PORT), timeout=5)
            t1 = threading.Thread(target=pipe, args=(client_sock, server_sock), daemon=True)
            t2 = threading.Thread(target=pipe, args=(server_sock, client_sock), daemon=True)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
        except Exception as e:
            print(f"[proxy] Connection to Streamlit failed: {e}", flush=True)
            try:
                client_sock.sendall(HEALTH_RESPONSE)
            except Exception:
                pass
            finally:
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
    print(f"[proxy] Listening on port {PROXY_PORT}", flush=True)
    while True:
        try:
            client_sock, _ = srv.accept()
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()
        except socket.timeout:
            continue
        except Exception:
            continue


def stream_output(pipe_obj, prefix):
    for line in iter(pipe_obj.readline, b''):
        text = line.decode('utf-8', errors='replace').rstrip()
        print(f"[{prefix}] {text}", flush=True)
    pipe_obj.close()


if __name__ == "__main__":
    proxy_thread = threading.Thread(target=start_proxy, daemon=True)
    proxy_thread.start()

    print("[proxy] Health check proxy ready on port 5000", flush=True)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(STREAMLIT_PORT),
            "--server.address", "127.0.0.1",
            "--server.headless", "true",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )

    threading.Thread(target=stream_output, args=(proc.stdout, "streamlit"), daemon=True).start()
    threading.Thread(target=stream_output, args=(proc.stderr, "streamlit-err"), daemon=True).start()
    threading.Thread(target=check_streamlit_ready, daemon=True).start()

    print("[proxy] Streamlit subprocess started, waiting...", flush=True)

    try:
        exit_code = proc.wait()
        print(f"[proxy] Streamlit exited with code {exit_code}", flush=True)
        if exit_code != 0:
            print("[proxy] Streamlit crashed — restarting in 5 seconds...", flush=True)
            time.sleep(5)
            os.execv(sys.executable, [sys.executable] + sys.argv)
    except KeyboardInterrupt:
        proc.terminate()
