import pdfplumber,glob,json,re
f=glob.glob('raw/C_*.pdf')[0]
S=1190.52/1819.0
cent={'bed_lic':1323,'bed_open':1388,'vent_lic':1457,'vent_open':1525,'day':1612}
cent={k:v*S for k,v in cent.items()}
rows=[]
with pdfplumber.open(f) as p:
    for pn,pg in enumerate(p.pages):
        ws=pg.extract_words()
        total=[w for w in ws if w['text']=='合計']
        ymax=total[0]['top']-2 if total else 1e9
        anchors=sorted([w for w in ws if re.fullmatch(r'\d{1,3}',w['text']) and w['x0']<190*S and w['top']<ymax],key=lambda w:w['top'])
        mids=[(a['top']+a['bottom'])/2 for a in anchors]
        for i,a in enumerate(anchors):
            lo=(mids[i-1]+mids[i])/2 if i else a['top']-6
            hi=(mids[i]+mids[i+1])/2 if i+1<len(anchors) else ymax
            band=[w for w in ws if lo<=(w['top']+w['bottom'])/2<hi and w is not a]
            code=[w for w in band if re.fullmatch(r'\d{10}',w['text'])][0]
            kinds=[w for w in band if w['text'] in('本院','日間照護','日間照')]
            kx=min(w['x0'] for w in kinds) if kinds else code['x1']+90*S
            phone_w=[w for w in band if w['text'].startswith('06') or re.fullmatch(r'\d{6,8}(#\d+)?',w['text']) and w['x0']>1100*S and w['x0']<1290*S]
            px=min(w['x0'] for w in phone_w) if phone_w else 1150*S
            name=''.join(w['text'] for w in sorted([w for w in band if w['x1']<code['x0']-1],key=lambda w:(round(w['top']/3),w['x0'])))
            dists=[w['text'] for w in sorted([w for w in band if code['x1']<=w['x0']<kx-1 and w['text'].endswith('區')],key=lambda w:w['top'])]
            ks=[w['text'] for w in sorted(kinds,key=lambda w:w['top'])]
            aw=[w for w in band if kx+25*S<=w['x0']<px-2]
            lines={}
            for w in aw: lines.setdefault(round(w['top']/4),[]).append(w)
            addrs=[''.join(x['text'] for x in sorted(l,key=lambda x:x['x0'])) for _,l in sorted(lines.items())]
            ph=''.join(w['text'] for w in sorted([w for w in band if px-1<=w['x0']<1285*S],key=lambda w:w['x0']))
            r={'no':int(a['text']),'name':name,'code':code['text'],'district':dists[0] if dists else '','kinds':ks,'districts':dists,'addresses':addrs,'phone':ph}
            for k in cent: r[k]=''
            for w in band:
                if w['x0']>=1285*S and re.fullmatch(r'\d+',w['text']):
                    k=min(cent,key=lambda k:abs((w['x0']+w['x1'])/2-cent[k])); r[k]=w['text']
            rows.append(r)
rows.sort(key=lambda r:r['no'])
json.dump(rows,open('work/C_rows.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print(len(rows),'rows; no range',rows[0]['no'],rows[-1]['no'],'unique codes',len({r['code'] for r in rows}))
def num(v): return int(v) if v else 0
print('sum bed_lic',sum(num(r['bed_lic']) for r in rows),'(PDF 6247)  sum bed_open',sum(num(r['bed_open']) for r in rows),'(6078)  vent',sum(num(r['vent_lic']) for r in rows),sum(num(r['vent_open']) for r in rows),'(27/27)  day',sum(num(r['day']) for r in rows),'(50)')
for r in rows:
    bad=[]
    if not r['addresses']: bad.append('NOADDR')
    if not r['phone']: bad.append('NOPHONE')
    if not r['bed_lic']: bad.append('NOBED')
    if len(r['addresses'])>1 or len(r['kinds'])>1 or bad: print(r['no'],r['name'],r['district'],r['kinds'],r['addresses'],r['phone'],r['bed_lic'],r['bed_open'],r['day'],bad)
