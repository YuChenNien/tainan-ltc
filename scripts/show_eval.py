import json
r=json.load(open('work/_report.json',encoding='utf-8'))
print('G total',r['g_total'],'unmatched',len(r['g_unmatched']))
for n in r['g_unmatched']: print('  G未對上:',n)
print('check',len(r['eval_check']))
for e in r['eval_check']: print(' ',e[0],e[1][:30],'|',e[2],'|',e[3][:70])
