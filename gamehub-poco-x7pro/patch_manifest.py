#!/usr/bin/env python3
"""Patch com falha segura: android:extractNativeLibs no manifesto Android binário."""
import struct,sys
def u16(b,p): return struct.unpack_from('<H',b,p)[0]
def u32(b,p): return struct.unpack_from('<I',b,p)[0]
def len8(b,p):
 v=b[p];p+=1
 if v&128: v=((v&127)<<8)|b[p];p+=1
 return v,p
def len16(b,p):
 v=u16(b,p);p+=2
 if v&32768: v=((v&32767)<<16)|u16(b,p);p+=2
 return v,p
def strings(b,s):
 h=u16(b,s+2);n=u32(b,s+8);f=u32(b,s+16);start=u32(b,s+20)
 if n>100000: raise ValueError('String pool invalid')
 a=[]
 for i in range(n):
  p=s+start+u32(b,s+h+4*i)
  if f&256:
   _,p=len8(b,p);k,p=len8(b,p);a.append(b[p:p+k].decode('utf8'))
  else:
   k,p=len16(b,p);a.append(b[p:p+2*k].decode('utf-16le'))
 return a
def patch_manifest(data):
 b=bytearray(data)
 if u16(b,0)!=3 or u32(b,4)!=len(b): raise ValueError('Expected Android binary AXML')
 off=u16(b,2);names=None;count=0
 while off<len(b):
  typ=u16(b,off);size=u32(b,off+4)
  if size<8 or size>len(b)-off:raise ValueError('Invalid XML chunk')
  if typ==1: names=strings(b,off)
  if typ==0x0102:
   if names is None: raise ValueError('No string pool')
   if names[u32(b,off+20)]=='application':
    ao=u16(b,off+24);sz=u16(b,off+26);cnt=u16(b,off+28)
    for j in range(cnt):
     p=off+16+ao+j*sz;ni=u32(b,p+4)
     if ni<len(names) and names[ni]=='extractNativeLibs':
      if u16(b,p+12)!=8 or b[p+15]!=0x12 or u32(b,p+16)!=0xffffffff:
       raise ValueError('Unexpected extractNativeLibs value')
      struct.pack_into('<I',b,p+16,0);count+=1
  off+=size
 if count!=1: raise ValueError('Expected one extractNativeLibs=true, found '+str(count))
 return bytes(b)
if __name__=='__main__':
 if len(sys.argv)!=3:raise SystemExit('usage: patch_manifest.py input output')
 open(sys.argv[2],'wb').write(patch_manifest(open(sys.argv[1],'rb').read()))
