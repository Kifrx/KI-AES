import socket
from AES import aes_encrypt

print("=== KONFIGURASI KDC  ===")
pilihan = input("Generate key manual or auto? (y=manual / n=auto) [y/N]: ").strip().lower()

if pilihan == 'y':
    K_A = input("Masukkan Master Key Alice (Ka): ").strip()
    K_B = input("Masukkan Master Key Bob (Kb)  : ").strip()
    K_S = input("Masukkan Session Key (Ks)     : ").strip()
else:
    print("[INFO] Menggunakan kunci default (Auto)...")
    K_A = "0x11111111111111111111111111111111"
    K_B = "0x22222222222222222222222222222222"
    K_S = "0x99999999999999999999999999999999"

HOST = '0.0.0.0'
PORT = 5050

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"\n[KDC] Server KDC berjalan di port {PORT}...")

conn, addr = server.accept()
print(f"[KDC] Terhubung dengan Alice dari {addr}")

# Terima ID_A || ID_B || N1 dari Alice
data = conn.recv(1024).decode()
id_a, id_b, n1 = data.split("||")
print(f"[KDC]  Diterima: ID_A={id_a}, ID_B={id_b}, N1={n1}")

# Enkripsi Balasan
isi_paket_a = f"{K_S}||{id_a}||{id_b}||{n1}"
enc_paket_a = aes_encrypt(isi_paket_a, K_A)

isi_tiket_b = f"{K_S}||{id_a}"
enc_tiket_b = aes_encrypt(isi_tiket_b, K_B)

pesan_balasan = f"{enc_paket_a}||{enc_tiket_b}"
conn.send(pesan_balasan.encode())
print("[KDC]  Pesan terenkripsi dikirim ke Alice.")

conn.close()
server.close()