import socket
from AES import aes_encrypt, aes_decrypt

print("=== KONFIGURASI BOB   ===")
pilihan = input("Generate key manual or auto? (y=manual / n=auto) [y/N]: ").strip().lower()

if pilihan == 'y':
    K_B = input("Masukkan Master Key Bob (Kb): ").strip()
    N2 = input("Masukkan Nonce N2 (bebas)   : ").strip()
else:
    print("[INFO] Menggunakan kunci & nonce default (Auto)...")
    K_B = "0x22222222222222222222222222222222"
    N2 = "123456"

HOST = '0.0.0.0'
PORT = 5001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"\n[BOB] Server Bob berjalan di port {PORT}...")

conn, addr = server.accept()
print(f"[BOB] Terhubung dengan Alice dari {addr}")

# Menerima Tiket dari Alice
tiket_hex = conn.recv(1024).decode()
print(f"[BOB] Tiket Diterima: {tiket_hex}")

hasil_dekripsi = aes_decrypt(tiket_hex, K_B)
k_s, id_a = hasil_dekripsi.split("||")
print(f"[BOB] Tiket Berhasil Didekripsi! Dapat Session Key (Ks): {k_s} dari ID_A: {id_a}")

# Kirim Challenge E(Ks, N2) ke Alice
enc_n2 = aes_encrypt(N2, k_s)
conn.send(enc_n2.encode())
print(f"[BOB] Challenge N2 ({N2}) dikirim ke Alice.")

# Menerima Respon E(Ks, f(N2)) dari Alice
respon_hex = conn.recv(1024).decode()
fn2_hasil = aes_decrypt(respon_hex, k_s)
print(f"[BOB] Respon Diterima: f(N2) = {fn2_hasil}")

if int(fn2_hasil) == int(N2) - 1:
    print("[BOB] AUTENTIKASI BERHASIL! Saluran aman siap digunakan.")
else:
    print("[BOB] AUTENTIKASI GAGAL!")

conn.close()
server.close()