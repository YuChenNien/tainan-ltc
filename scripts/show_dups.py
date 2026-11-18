import json
R={r['id']:r for r in json.load(open('work/institutions.json',encoding='utf-8'))}
rep=json.load(open('work/_report.json',encoding='utf-8'))
for a,an,b,bn,why in rep['dups']:
    if why!='電話相同' or a.startswith('TN-N') or b.startswith('TN-N'):
        for i in (a,b):
            r=R[i]; print(i,r['name'],'|',r['address'],'|',r['phone'],'|床',r['beds_licensed'],r['sub_type'],r['eval_grade'])
        print('  =>',why)
