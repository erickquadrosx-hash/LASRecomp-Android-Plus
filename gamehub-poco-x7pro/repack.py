#!/usr/bin/env python3
"""GameHub 6.3.2: only transform native packaging for 16KiB loading on Android."""
import argparse,hashlib,zipfile,struct,os
from patch_manifest import patch_manifest
EXPECTED='e51456bd3fb1c041dbdf3c756878ce1ddb37dfdb933b266142b22354b7d50ed2'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def clone(i):
 o=zipfile.ZipInfo(i.filename,i.date_time)
 for k in ('compress_type','comment','create_system','external_attr','internal_attr','flag_bits'): setattr(o,k,getattr(i,k))
 o.extra=i.extra
 return o
def main(src,dst):
 if sha(src)!=EXPECTED:raise SystemExit('SHA256 mismatch. Aborting.')
 with zipfile.ZipFile(src) as zi,zipfile.ZipFile(dst,'w',allowZip64=False) as zo:
  if zi.testzip() is not None:raise ValueError('Invalid source ZIP')
  for i in zi.infolist():
   n=i.filename
   if n=='META-INF/MANIFEST.MF' or (n.startswith('META-INF/') and n.upper().endswith(('.SF','.RSA','.DSA','.EC'))):
    continue
   data=zi.read(i);o=clone(i)
   if n=='AndroidManifest.xml':data=patch_manifest(data)
   if n.startswith('lib/arm64-v8a/') and n.endswith('.so'):
    o.compress_type=zipfile.ZIP_STORED
    pad=(-(zo.fp.tell()+30+len(n.encode('utf8'))+len(o.extra)+4))%16384
    o.extra+=struct.pack('<HH',0xd935,pad)+bytes(pad)
   with zo.open(o,'w',force_zip64=False) as f:f.write(data)
 with zipfile.ZipFile(dst) as z:
  assert z.testzip() is None
  libs=[i for i in z.infolist() if i.filename.startswith('lib/arm64-v8a/') and i.filename.endswith('.so')]
  if len(libs)!=25:raise RuntimeError('Expected 25 native libs')
  for i in libs:
   ofs=i.header_offset+30+len(i.filename.encode('utf8'))+len(i.extra)
   if i.compress_type!=0 or ofs%16384:raise ValueError('Native alignment failed: '+i.filename)
 print('OK: 25 libs, ZIP CRC, 16KiB aligned; size:',os.path.getsize(dst))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('unsigned');a=p.parse_args();main(a.source,a.unsigned)
