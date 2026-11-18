import pdfplumber,sys,glob
f=glob.glob(sys.argv[1])[0]
with pdfplumber.open(f) as p:
    print(len(p.pages),'pages')
    for i,pg in enumerate(p.pages[:int(sys.argv[2])]):
        for t in pg.extract_tables():
            print('--page',i+1,'rows',len(t))
            for r in t[:int(sys.argv[3])]: print([ (c or '').replace('\n','|') for c in r])
