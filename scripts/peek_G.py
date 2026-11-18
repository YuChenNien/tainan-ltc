import zipfile,glob,re
f=glob.glob('raw/G_*.ods')[0]
x=zipfile.ZipFile(f).read('content.xml').decode('utf-8')
rows=re.findall(r'<table:table-row[^>]*>(.*?)</table:table-row>',x,flags=re.S)
print(len(rows))
out=[]
for r in rows:
    cells=re.findall(r'<table:table-cell([^>]*?)(?:/>|>(.*?)</table:table-cell>)',r,flags=re.S)
    vals=[]
    for attrs,inner in cells:
        rep=re.search(r'number-columns-repeated="(\d+)"',attrs); n=int(rep.group(1)) if rep else 1
        t=re.sub(r'<[^>]+>','',inner or '')
        vals+= [t]*min(n,3)
    out.append(vals)
for v in out[:12]: print(v)
