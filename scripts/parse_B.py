import pdfplumber,glob,json,re
f=glob.glob('raw/B_*.pdf')[0]
rows=[]
with pdfplumber.open(f) as p:
    for t in p.pages[0].extract_tables():
        for r in t:
            if r[0] and r[0].strip().isdigit():
                c=[(x or '').replace('\n','') for x in r]
                rows.append({'no':int(c[0]),'district':c[1],'name':c[2],'est_date':c[3],'phone':c[6],'address':c[7],
                  'beds_licensed':int((r[8] or '').split(chr(10))[0]),'beds_open':int((r[9] or '').split(chr(10))[0]),'target_raw':'|'.join((r[8] or '').split(chr(10))[1:]),'beds_detail_open':'|'.join((r[9] or '').split(chr(10))[1:]),'extra_services':c[10],'eval_raw':c[11]})
json.dump(rows,open('work/B_rows.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(rows))
for r in rows: print(r['no'],r['district'],r['name'][:20],r['phone'][:30],r['address'][:30],r['beds_licensed'],r['beds_open'],r['eval_raw'])
