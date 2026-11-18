import json, glob, re, collections, os

PENDING = '待確認'
SRC_DATE = {'A': '2026-11-18（社會局頁面更新日）', 'B': '2026-09-21公告（內文115年7月21日更新）', 'C': '2026-08-18公告（製表日115/08/17）'}
SRC_NAME = {'A': '臺南市政府社會局「社會福利機構空位查詢」開放資料', 'B': '臺南市政府衛生局「住宿式長照機構一覽表」', 'C': '臺南市政府衛生局「一般護理之家名冊」'}

CN = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}


def cn_num(t):
    if t == '十':
        return 10
    if '十' in t:
        a, b = t.split('十')
        return (CN[a] if a else 1) * 10 + (CN[b] if b else 0)
    return CN[t] if len(t) == 1 else None


def cn2d(s):
    def rep(m):
        n = cn_num(m.group(1))
        return (str(n) if n else m.group(1)) + m.group(2)
    return re.sub(r'([一二三四五六七八九十]+)(段|街|路)', rep, s)


def norm_addr(a):
    a = a.strip().replace('台南', '臺南').replace('（', '(').replace('）', ')').replace('～', '~')
    a = re.sub(r'^\d{3,6}(?=臺南)', '', a)
    if not a.startswith('臺南市'):
        a = '臺南市' + a
    a = re.sub(r'\s+', '', a)
    return cn2d(a)


def addr_key(a):
    a = norm_addr(a)
    a = re.sub(r'\d+鄰', '', a)
    a = re.sub(r'(?<=區)[^區路街道巷弄號]{1,4}里', '', a)
    m = re.match(r'臺南市(\S{1,3}區)(.*?)(\d+(?:-\d+)?(?:之\d+)?號)', a)
    return (m.group(1) + m.group(2) + m.group(3)) if m else a


def phone_key(p):
    s = ''.join(re.findall(r'\d+', p))
    if len(s) >= 9 and s.startswith('06'):
        s = s[2:]
    return s[-7:] if len(s) >= 7 else s


def district_of(addr):
    m = re.match(r'臺南市(\S{1,3}區)', addr)
    return m.group(1) if m else ''


A = json.load(open(glob.glob('raw/A_*.json')[0], encoding='utf-8'))
B = json.load(open('work/B_rows.json', encoding='utf-8'))
C = json.load(open('work/C_rows.json', encoding='utf-8'))

recs = []
excluded = []
catc = collections.Counter(x['類別'] for x in A)

# ---- A 老福機構
for x in A:
    if x['類別'] != '老福機構':
        excluded.append({'source': 'A', 'name': x['機構名稱'], 'reason': '非住宿機構類別（%s）' % x['類別']})
        continue
    s = x['核定服務人數[床位]']
    name = x['機構名稱']
    if '歇業' in s or '歇業' in name:
        excluded.append({'source': 'A', 'name': name, 'reason': '已歇業（社會局資料）：' + (s or name)})
        continue
    c = x['聯絡方式'].strip()
    if re.match(r'^[\d\(\)\-\s]+/', c):
        ph, ad = [t.strip() for t in c.split('/', 1)]
    else:
        ad, ph = [t.strip() for t in c.rsplit('/', 1)]
    yh = re.search(r'(?:養護)+(\d+)', s)
    an = re.search(r'安養(\d+)', s)
    yh_n = int(yh.group(1)) if yh else None
    an_n = int(an.group(1)) if an else None
    if yh_n is None and an_n is None:
        m2 = re.match(r'(\d+)\s*床', s)
        if m2 and '養護' in name:
            yh_n = int(m2.group(1))
        if m2 and '安養' in name:
            an_n = int(m2.group(1))
    kinds = [k for k, n in (('養護', yh_n), ('安養', an_n)) if n]
    types = '、'.join(kinds) if kinds else PENDING
    tube = re.search(r'含管路[^\d]*(\d+)\s*床', s.replace(' ', ''))
    tot = (yh_n or 0) + (an_n or 0)
    vac_raw = x['可申請服務人數[床位]'].strip()
    nums = [int(t) for t in re.findall(r'\d+', vac_raw)]
    vac = sum(nums) if nums else None
    ev = x['最近一次評鑑[查核]結果'].strip()
    if ev in ('優', '甲', '乙', '丙'):
        grade, evy = ev, PENDING
    elif '許可設立' in ev:
        grade, evy = '新設立，尚無評鑑', '—'
    else:
        grade, evy = PENDING, PENDING
    recs.append({'src': 'A', 'nat': x['連結網址'].split('s=')[-1], 'name': name, 'category': '老人福利機構', 'sub_type': types,
                 'district': district_of(norm_addr(ad)), 'address': norm_addr(ad), 'phone': ph, 'beds_licensed': tot or None,
                 'beds_licensed_text': s, 'beds_open': None, 'vacancy': vac, 'vacancy_text': vac_raw,
                 'tube_beds': int(tube.group(1)) if tube else None, 'target': x['服務對象'],
                 'eval_kind': '老人福利機構評鑑／查核（社會局）', 'eval_grade': grade, 'eval_year': evy, 'eval_raw': ev,
                 'fee': '待確認（社會局未公告收費）', 'shelter_bed_raw': x['收容床'], 'detail_url': x['連結網址'], 'extra': ''})

# ---- B 住宿式長照機構
for r in B:
    ev = r['eval_raw']
    mm = re.match(r'(\d+)年(合格|不合格)', ev)
    grade, evy = (mm.group(2), mm.group(1) + '年') if mm else ('未評鑑', '—')
    ad = norm_addr(r['address'])
    recs.append({'src': 'B', 'nat': r['name'], 'name': r['name'], 'category': '住宿式長照機構', 'sub_type': '住宿式長照',
                 'district': r['district'] or district_of(ad), 'address': ad, 'phone': r['phone'],
                 'beds_licensed': r['beds_licensed'], 'beds_licensed_text': '', 'beds_open': r['beds_open'],
                 'vacancy': None, 'vacancy_text': '', 'tube_beds': None, 'target': r['target_raw'].replace('|', ''),
                 'eval_kind': '長期照顧服務機構評鑑（衛生局）', 'eval_grade': grade, 'eval_year': evy, 'eval_raw': ev,
                 'fee': '官方收費上限（衛生局115/7/8）', 'shelter_bed_raw': '', 'detail_url': '',
                 'extra': r['extra_services'].replace('|', '')})

# ---- C 護理之家
for r in C:
    ad = norm_addr(r['addresses'][0]) if r['addresses'] else ''
    extra = ''
    if len(r['addresses']) > 1:
        extra = '另有據點：' + '；'.join(norm_addr(a) for a in r['addresses'][1:]) + '（' + '、'.join(r['kinds'][1:]) + '）'
    recs.append({'src': 'C', 'nat': r['code'], 'name': r['name'], 'category': '護理之家', 'sub_type': '一般護理之家',
                 'district': r['district'], 'address': ad, 'phone': r['phone'], 'beds_licensed': int(r['bed_lic'] or 0),
                 'beds_licensed_text': '', 'beds_open': int(r['bed_open'] or 0), 'vacancy': None, 'vacancy_text': '',
                 'tube_beds': None, 'vent_licensed': int(r['vent_lic'] or 0), 'vent_open': int(r['vent_open'] or 0),
                 'day_open': int(r['day'] or 0), 'target': '', 'eval_kind': '（護理之家無評鑑）',
                 'eval_grade': '無評鑑資料', 'eval_year': '—', 'eval_raw': '', 'fee': '官方收費上限（衛生局115/7/8）',
                 'shelter_bed_raw': '', 'detail_url': '', 'extra': extra, 'org_code': r['code']})

# ---- G 老福機構歷年評鑑結果（補評鑑年度）
import zipfile
def read_ods(path):
    x = zipfile.ZipFile(path).read('content.xml').decode('utf-8')
    out = []
    for r in re.findall(r'<table:table-row[^>]*>(.*?)</table:table-row>', x, flags=re.S):
        vals = []
        for attrs, inner in re.findall(r'<table:table-cell([^>]*?)(?:/>|>(.*?)</table:table-cell>)', r, flags=re.S):
            m = re.search(r'number-columns-repeated="(\d+)"', attrs)
            n = int(m.group(1)) if m else 1
            vals += [re.sub(r'<[^>]+>', '', inner or '')] * min(n, 3)
        out.append(vals)
    return out

def nname(s):
    return re.sub(r'[\s()（）]|老人', '', s.replace('台', '臺'))

G_rows = []
g = read_ods(glob.glob('raw/G_*.ods')[0])
hdr = next(r for r in g if r and r[0] == '編號')
years = [(i, re.match(r'(\d+)年', h).group(1)) for i, h in enumerate(hdr) if re.match(r'\d+年評鑑結果', h)]
for r in g:
    if r and r[0].strip().isdigit() and len(r) > 7:
        hist = {}
        for i, yr in years:
            v = (r[i] if i < len(r) else '').strip()
            if v and v not in ('_', '-'):
                hist[yr] = v
        G_rows.append({'name': r[1], 'addr': r[5], 'phone': r[6], 'hist': hist})
g_by_name = {nname(x['name']): x for x in G_rows}
g_by_phone = collections.defaultdict(list)
for x in G_rows:
    g_by_phone[phone_key(x['phone'])].append(x)
eval_check = []
g_used = set()
for r in recs:
    if r['src'] != 'A':
        continue
    hit = g_by_name.get(nname(r['name']))
    how = '名稱'
    if not hit:
        cands = [x for x in g_by_phone.get(phone_key(r['phone']), []) if addr_key(x['addr']) == addr_key(r['address'])]
        hit, how = (cands[0], '電話＋地址') if cands else (None, '')
    if not hit:
        r['eval_history'] = {}
        eval_check.append((r, r['name'], '歷年評鑑一覽表查無對應', r['eval_raw']))
        continue
    g_used.add(hit['name'])
    r['eval_history'] = hit['hist']
    if hit['hist']:
        ly = max(hit['hist'], key=int)
        lv = hit['hist'][ly]
        lg = re.sub(r'\(.*?\)|（.*?）', '', lv)
        r['eval_year'] = ly + '年' + ('（複評）' if '複評' in lv else '')
        if r['eval_raw'] in ('優', '甲', '乙', '丙') and lg != r['eval_raw']:
            r['eval_year'] = PENDING
            eval_check.append((r, r['name'], '社會局空位表等第與歷年一覽表最新等第不同', '空位表=%s；一覽表=%s年%s' % (r['eval_raw'], ly, lv)))
        if r['eval_raw'] not in ('優', '甲', '乙', '丙'):
            r['eval_note'] = '歷年一覽表有紀錄：' + str(hit['hist'])
            r['eval_grade'] = lv
            eval_check.append((r, r['name'], '空位表無等第，採歷年一覽表最新紀錄', '%s年%s' % (ly, lv)))
    else:
        r['eval_year'] = '歷年一覽表無評鑑紀錄'
g_unmatched = [x['name'] for x in G_rows if x['name'] not in g_used]

# ---- 穩定編號
idmap = json.load(open('id_map.json', encoding='utf-8')) if os.path.exists('id_map.json') else {}
pref = {'A': 'TN-E', 'B': 'TN-L', 'C': 'TN-N'}
for r in recs:
    key = '%s:%s' % (r['src'], r['nat'])
    if key not in idmap:
        n = sum(1 for v in idmap.values() if v.startswith(pref[r['src']] + '-')) + 1
        idmap[key] = '%s-%03d' % (pref[r['src']], n)
    r['id'] = idmap[key]
    r['source_name'] = SRC_NAME[r['src']]
    r['source_date'] = SRC_DATE[r['src']]
json.dump(idmap, open('id_map.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ---- 地址與電話檢查
issues = []
for r in recs:
    d = district_of(r['address'])
    if not r['address']:
        issues.append((r['id'], r['name'], '缺地址'))
    elif d and r['district'] and d != r['district']:
        issues.append((r['id'], r['name'], '區別欄位=%s，地址=%s' % (r['district'], d)))
    if not r['phone']:
        issues.append((r['id'], r['name'], '缺電話'))

# ---- 疑似重複
dups = []
for i in range(len(recs)):
    for j in range(i + 1, len(recs)):
        a, b = recs[i], recs[j]
        why = []
        if a['address'] and b['address'] and addr_key(a['address']) == addr_key(b['address']):
            why.append('地址相同')
        pa, pb = phone_key(a['phone']), phone_key(b['phone'])
        if pa and pa == pb:
            why.append('電話相同')
        if a['name'] == b['name']:
            why.append('名稱相同')
        if why:
            dups.append((a['id'], a['name'], b['id'], b['name'], '、'.join(why)))

json.dump(recs, open('work/institutions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
eval_check = [(e[0]['id'],) + e[1:] for e in eval_check]
json.dump({'catcount': catc, 'excluded': excluded, 'issues': issues, 'dups': dups, 'eval_check': eval_check, 'g_unmatched': g_unmatched, 'g_total': len(G_rows)}, open('work/_report.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('G rows', len(G_rows), 'unmatched in G:', g_unmatched)
print('eval_check', len(eval_check))
for e in eval_check:
    print(' ', e)
print('A eval_year:', dict(collections.Counter(r['eval_year'] for r in recs if r['src'] == 'A')))

print('records', len(recs), dict(collections.Counter(r['category'] for r in recs)))
print('excluded', len(excluded), dict(collections.Counter(e['reason'].split('（')[0] for e in excluded)))
print('issues', len(issues))
for i in issues:
    print(' ', i)
print('dups', len(dups))
for d in dups:
    print(' ', d)
print('types A:', dict(collections.Counter(r['sub_type'] for r in recs if r['src'] == 'A')))
print('A no beds:', [(r['name'], r['beds_licensed_text']) for r in recs if r['src'] == 'A' and not r['beds_licensed']])
print('A grade:', dict(collections.Counter(r['eval_grade'] for r in recs if r['src'] == 'A')))
