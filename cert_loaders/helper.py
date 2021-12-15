
def create_chunked_cert(cert):
        chunk_size = 64
        # crt_string = base64_encode(crt)[0].decode("ascii").replace("\n",'')
        chunked = '\n'.join(cert[i:i+chunk_size] for i in range(0, len(cert), chunk_size))
        return f"-----BEGIN CERTIFICATE-----\n{chunked}\n-----END CERTIFICATE-----\n"
