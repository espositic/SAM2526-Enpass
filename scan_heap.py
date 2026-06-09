data = open(r"/home/kali/Desktop/enpass.hprof", "rb").read()
print("heap size:", len(data))

def count(needle):
    a = data.count(needle.encode("latin1"))
    u = data.count(needle.encode("utf-16-le"))
    return a, u

for s in ["password2026", "testtest", "ZTEST", "passwordpassword"]:
    a, u = count(s)
    print(f"{s!r:20} ASCII={a}  UTF16LE={u}")

# contesto attorno alla prima occorrenza ASCII della master password
i = data.find(b"password2026")
if i >= 0:
    seg = data[i-8:i+20]
    print("contesto password2026:", seg)
