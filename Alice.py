import socket
from AES import aes_encrypt, aes_decrypt

print("=== KONFIGURASI ALICE   ===")
pilihan = input("Generate key manual or auto? (y=manual / n=auto) [y/N]: ").strip().lower()

if pilihan == 'y':
    K_A = input("Masukkan Master Key Alice (Ka): ").strip()
    IP_KDC = input("Masukkan IP KDC              : ").strip()
    IP_BOB = input("Masukkan IP Bob              : ").strip()
    N1 = input("Masukkan Nonce N1 (bebas)    : ").strip()
else:
    print("[INFO] Menggunakan kunci & IP default (Auto)...")
    K_A = "0x11111111111111111111111111111111"
    IP_KDC = "192.168.80.1" 
    IP_BOB = "192.168.80.130" 
    N1 = "987654"

ID_A = "Alice"
ID_B = "Bob"

print(f"\n[ALICE] Mengubungi KDC ({IP_KDC}:5050)...")
soc_kdc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc_kdc.connect((IP_KDC, 5050))

# Request ke KDC
pesan_req = f"{ID_A}||{ID_B}||{N1}"
soc_kdc.send(pesan_req.encode())

# Terima Balasan dari KDC
balasan_kdc = soc_kdc.recv(2048).decode()
enc_paket_a, tiket_b = balasan_kdc.split("||")

hasil_dekripsi = aes_decrypt(enc_paket_a, K_A)
k_s, recv_ida, recv_idb, recv_n1 = hasil_dekripsi.split("||")

if recv_n1 == N1:
    print(f"[ALICE] Berhasil Dekripsi dari KDC! Dapat Session Key (Ks): {k_s}")
soc_kdc.close()

print(f"\n[ALICE] Mengubungi Bob ({IP_BOB}:5001)...")
soc_bob = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc_bob.connect((IP_BOB, 5001))

# Teruskan Tiket ke Bob
soc_bob.send(tiket_b.encode())
print("[ALICE] Tiket dikirim ke Bob.")

# Terima Challenge N2 dari Bob
enc_n2 = soc_bob.recv(1024).decode()
n2 = aes_decrypt(enc_n2, k_s)
print(f"[ALICE] Diterima Challenge N2: {n2}")

# Hitung f(N2) = N2 - 1
fn2 = str(int(n2) - 1)
enc_fn2 = aes_encrypt(fn2, k_s)
soc_bob.send(enc_fn2.encode())
print(f"[ALICE] Respon f(N2) = {fn2} dikirim balik ke Bob.")

soc_bob.close()