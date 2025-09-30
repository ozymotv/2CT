# kmnet_wrapper.py
import ctypes
import os

_km = None
def init_kmnet(uuid: str, ip: str, port: int) -> bool:
    global _km
    if _km:                    # already loaded
        return True
    dll_path = os.path.join(os.path.dirname(__file__),
                            'kmNet.cp310-win_amd64.pyd')
    try:
        _km = ctypes.CDLL(dll_path)
        return _km.Init(bytes(uuid, 'utf-8'),
                        bytes(ip, 'utf-8'),
                        ctypes.c_uint16(port)) == 0
    except Exception as e:
        print(f'KMNet load error: {e}')
        _km = None
        return False

def click_mouse(button: int = 1):
    """button: 1-left, 2-right"""
    if _km:
        _km.Click(ctypes.c_int(button))
