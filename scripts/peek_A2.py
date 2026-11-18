import json,glob,re
d=json.load(open(glob.glob('raw/A_*.json')[0],encoding='utf-8'))
lf=[x for x in d if x['類別']=='老福機構']
for x in lf:
    s=x['核定服務人數[床位]']
    if not re.fullmatch(r'養護\d+\(含管路(、胃造廔口)?\d+床\)',s):
        print(repr(x['機構名稱']),repr(s),'|空',x['可申請服務人數[床位]'],'|',x['最近一次評鑑[查核]結果'][:12],'|',x['聯絡方式'][:50])
