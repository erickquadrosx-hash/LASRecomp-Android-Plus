"""Align uncompressed APK entries before APK v2 signing. Byte preserving; no game data."""
import struct
import zipfile
from pathlib import Path

def align_zip(source, destination, alignment=4):
    data=Path(source).read_bytes()
    end=data.rfind(b'PK\x05\x06')
    if end<0:raise ValueError("Missing ZIP end record")
    count=struct.unpack_from('<H',data,end+10)[0]
    cd=struct.unpack_from('<I',data,end+16)[0]
    with zipfile.ZipFile(source) as z:
        members=sorted(z.infolist(),key=lambda info:info.header_offset)
    if len(members)!=count:raise ValueError("ZIP member count mismatch")
    dest=bytearray(data[:members[0].header_offset])
    old_to_new={}
    for idx,member in enumerate(members):
        old=member.header_offset
        stop=members[idx+1].header_offset if idx+1<len(members) else cd
        block=data[old:stop]
        if block[:4]!=b'PK\x03\x04':raise ValueError("Invalid local header")
        fn,extra=struct.unpack_from('<HH',block,26)
        position=len(dest)+30+fn+extra
        pad=0
        if member.compress_type==0 and position%alignment:
            pad=4+((-position-4)%alignment)
        old_to_new[old]=len(dest)
        if pad:
            padding=struct.pack('<HH',0xffff,pad-4)+b'\0'*(pad-4)
            block=(block[:28]+struct.pack('<H',extra+pad)+block[30:30+fn+extra]
                   +padding+block[30+fn+extra:])
        dest+=block
    new_cd=len(dest)
    cur=cd
    for _ in range(count):
        if data[cur:cur+4]!=b'PK\x01\x02':raise ValueError("Invalid central directory")
        fn,ext,comment=struct.unpack_from('<HHH',data,cur+28)
        size=46+fn+ext+comment
        entry=bytearray(data[cur:cur+size])
        struct.pack_into('<I',entry,42,old_to_new[struct.unpack_from('<I',entry,42)[0]])
        dest+=entry
        cur+=size
    if cur!=end:raise ValueError("Unexpected ZIP central-directory length")
    eocd=bytearray(data[end:])
    struct.pack_into('<I',eocd,16,new_cd)
    dest+=eocd
    Path(destination).write_bytes(dest)
    with zipfile.ZipFile(destination) as result:
        if result.testzip() is not None:raise ValueError("CRC mismatch")
        with open(destination,'rb') as fh:
            for member in result.infolist():
                if member.compress_type!=0:continue
                fh.seek(member.header_offset)
                h=fh.read(30)
                name,extra=struct.unpack_from('<HH',h,26)
                if (member.header_offset+30+name+extra)%alignment!=0:
                    raise ValueError("Stored entry misaligned: "+member.filename)
