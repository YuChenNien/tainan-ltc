import pdfplumber,sys,glob
f=glob.glob(sys.argv[1])[0]
with pdfplumber.open(f) as p:
    pg=p.pages[int(sys.argv[2])]
    pg.to_image(resolution=int(sys.argv[3])).save(sys.argv[4])
    print(pg.width,pg.height)
