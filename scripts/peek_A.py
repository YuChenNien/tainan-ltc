import json,glob,collections,re
d=json.load(open(glob.glob('raw/A_*.json')[0],encoding='utf-8'))
lf=[x for x in d if x['類別']=='老福機構']
print(len(lf)); print(list(lf[0].keys()))
for k in ['核定服務人數[床位]','可申請服務人數[床位]','最近一次評鑑[查核]結果','收容床']:
    c=collections.Counter(x[k] for x in lf); print(k,len(c),c.most_common(6))
print(collections.Counter(re.sub(r'\d+','N',x['核定服務人數[床位]']) for x in lf).most_common(15))
bad=[x['聯絡方式'] for x in lf if not re.search(r'/\s*[\d\-\(\)#,、 ]+$',x['聯絡方式'])]
print('contact not ending with phone:',len(bad),bad[:5])
for x in lf[:4]: print(x['機構名稱'],'|',x['聯絡方式'])
print([x['機構名稱'] for x in lf if '評鑑' in x['最近一次評鑑[查核]結果'] or len(x['最近一次評鑑[查核]結果'])>2])
dup=collections.Counter(x['機構名稱'] for x in lf); print('dup names',[k for k,v in dup.items() if v>1])
