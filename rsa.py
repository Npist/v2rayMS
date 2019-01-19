import rsa

# 生成密钥
(pubkey, privkey) = rsa.newkeys(1024)

# 保存密钥
with open('public.pem', 'w+') as f:
    f.write(pubkey.save_pkcs1().decode())

with open('private.pem', 'w+') as f:
    f.write(privkey.save_pkcs1().decode())
