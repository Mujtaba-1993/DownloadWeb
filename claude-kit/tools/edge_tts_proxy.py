import sys, certifi, asyncio
certifi.where = lambda: '/root/.ccr/ca-bundle.crt'
import edge_tts
v, rate, pitch, text, out = sys.argv[1:6]
asyncio.run(edge_tts.Communicate(text, v, rate=rate, pitch=pitch, proxy=__import__('os').environ.get('HTTPS_PROXY')).save(out))
