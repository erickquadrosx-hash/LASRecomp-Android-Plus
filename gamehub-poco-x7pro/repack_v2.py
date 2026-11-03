#!/usr/bin/env python3
"""Exact-source GameHub 6.3.2 packer. Fix .arsc alignment and native 16KiB.
Does NOT change Steam/Epic/GOG resources, runtime drivers, or PC emulation.
"""
import argparse,hashlib,zipfile,struct
from patch_manifest import patch_manifest
EXPECTED='e51456bd3fb1c041dbdf3c756878ce1ddb37dfdb933b266142b22354b7d50ed2'
def sha(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def data_start(fp,i):
 fp.seek(i.header_offset)
 h=fp.read(30)
 if h[:4]!=b'PK\x03\x04':raise ValueError('bad local ZIP header')
 n,e=struct.unpack_from('<HH',h,26)
 return i.header_offset+30+n+e
def build(src,out,mode):
 if sha(src)!=EXPECTED:raise ValueError('Source SHA256 mismatch')
 with zipfile.ZipFile(src) as z,zipfile.ZipFile(out,'w',allowZip64=False) as dst:
  if z.testzip():raise ValueError('Source ZIP failed CRC')
  for i in z.infolist():
   if i.filename=='META-INF/MANIFEST.MF' or (i.filename.startswith('META-INF/') and i.filename.upper().endswith(('.SF','.RSA','.DSA','.EC'))):continue
   new=zipfile.ZipInfo(i.filename,i.date_time)
   for k in ('compress_type','comment','create_system','external_attr','internal_attr','flag_bits'):setattr(new,k,getattr(i,k))
   new.extra=i.extra
   b=z.read(i)
   if mode=='native16k':
    if i.filename=='AndroidManifest.xml':b=patch_manifest(b)
    if i.filename.startswith('lib/arm64-v8a/') and i.filename.endswith('.so'):new.compress_type=zipfile.ZIP_STORED
   if new.compress_type==zipfile.ZIP_STORED:
    alignment=16384 if mode=='native16k' and i.filename.startswith('lib/arm64-v8a/') and i.filename.endswith('.so') else 4
    base=dst.fp.tell()+30+len(new.filename.encode('utf8'))+len(new.extra)
    pad=(-(base+4))%alignment
    new.extra+=struct.pack('<HH',0xd935,pad)+bytes(pad)
   with dst.open(new,'w',force_zip64=False) as f:f.write(b)
 with zipfile.ZipFile(src) as z,zipfile.ZipFile(out) as dst,open(out,'rb') as f:
  if dst.testzip():raise ValueError('Output CRC failure')
  actual=dst.getinfo('resources.arsc')
  if actual.compress_type!=0 or data_start(f,actual)%4:raise ValueError('resources.arsc not 4-byte aligned')
  lib=0
  for i in z.infolist():
   if i.filename not in dst.namelist():continue
   x=dst.getinfo(i.filename)
   if i.filename!='AndroidManifest.xml' or mode=='compat':
    if z.read(i)!=dst.read(x):raise ValueError('content change: '+i.filename)
   if x.compress_type==0:
    align=16384 if mode=='native16k' and i.filename.startswith('lib/arm64-v8a/') and i.filename.endswith('.so') else 4
    if data_start(f,x)%align:raise ValueError('Unaligned: '+i.filename)
   if i.filename.startswith('lib/arm64-v8a/') and i.filename.endswith('.so'):lib+=1
  if lib!=25:raise ValueError('Expected 25 ARM64 native libraries')
 print('Verified',mode,sha(out))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('unsigned');p.add_argument('--mode',choices=['compat','native16k'],default='native16k');a=p.parse_args();build(a.source,a.unsigned,a.mode)
