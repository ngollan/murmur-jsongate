import Ice, os

MURMUR_SLICE_PATH = '/usr/share/slice/Murmur.ice'
if 'MURMUR_SLICE_PATH' in os.environ:
	MURMUR_SLICE_PATH = os.environ['MURMUR_SLICE_PATH']

Ice.loadSlice(MURMUR_SLICE_PATH)
import Murmur
