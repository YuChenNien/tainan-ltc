import raw from '../../data/work/institutions.json';

export type Inst = {
  id: string; src: 'A' | 'B' | 'C'; name: string; category: string; sub_type: string;
  district: string; address: string; phone: string;
  beds_licensed: number | null; beds_open: number | null; vacancy: number | null; vacancy_text: string;
  tube_beds: number | null; target: string; extra: string;
  eval_kind: string; eval_grade: string; eval_year: string;
  fee: string; source_name: string; source_date: string;
  vent_licensed?: number; vent_open?: number; day_open?: number;
  eval_history?: Record<string, string>; detail_url?: string; beds_licensed_text?: string;
};

export const insts = raw as unknown as Inst[];

// ---- 圖示：同一個名稱可在兩套圖示庫之間切換（步驟 2 讓你比較後選一套）
export const ICON_SET: 'lucide' | 'tabler' = 'tabler';
export const ICONS: Record<string, { lucide: string; tabler: string }> = {
  welfare: { lucide: 'lucide:heart-handshake', tabler: 'tabler:heart-handshake' },
  nursing: { lucide: 'lucide:stethoscope', tabler: 'tabler:stethoscope' },
  ltc: { lucide: 'lucide:bed-double', tabler: 'tabler:bed' },
  bed: { lucide: 'lucide:bed-double', tabler: 'tabler:bed' },
  home: { lucide: 'lucide:house', tabler: 'tabler:home' },
  pin: { lucide: 'lucide:map-pin', tabler: 'tabler:map-pin' },
  phone: { lucide: 'lucide:phone', tabler: 'tabler:phone' },
  money: { lucide: 'lucide:banknote', tabler: 'tabler:cash' },
  shield: { lucide: 'lucide:shield-check', tabler: 'tabler:shield-check' },
  award: { lucide: 'lucide:award', tabler: 'tabler:award' },
  badge: { lucide: 'lucide:badge-check', tabler: 'tabler:rosette-discount-check' },
  ok: { lucide: 'lucide:circle-check', tabler: 'tabler:circle-check' },
  bad: { lucide: 'lucide:circle-x', tabler: 'tabler:circle-x' },
  warn: { lucide: 'lucide:triangle-alert', tabler: 'tabler:alert-triangle' },
  unknown: { lucide: 'lucide:circle-help', tabler: 'tabler:help-circle' },
  users: { lucide: 'lucide:users', tabler: 'tabler:users' },
  calendar: { lucide: 'lucide:calendar', tabler: 'tabler:calendar' },
  link: { lucide: 'lucide:external-link', tabler: 'tabler:external-link' },
  search: { lucide: 'lucide:search', tabler: 'tabler:search' },
  compare: { lucide: 'lucide:columns-2', tabler: 'tabler:columns-2' },
  calc: { lucide: 'lucide:calculator', tabler: 'tabler:calculator' },
  nophoto: { lucide: 'lucide:image-off', tabler: 'tabler:photo-off' },
  info: { lucide: 'lucide:info', tabler: 'tabler:info-circle' },
  brain: { lucide: 'lucide:brain', tabler: 'tabler:brain' },
  tube: { lucide: 'lucide:syringe', tabler: 'tabler:vaccine' },
  sofa: { lucide: 'lucide:sofa', tabler: 'tabler:armchair' },
  map: { lucide: 'lucide:map', tabler: 'tabler:map-2' },
  file: { lucide: 'lucide:file-text', tabler: 'tabler:file-text' },
  arrow: { lucide: 'lucide:arrow-right', tabler: 'tabler:arrow-right' },
};

// ---- 單位類型（網頁上的分類，順序即顯示順序）
export const TYPES = [
  { key: '老人福利機構', short: '老人福利機構', icon: 'welfare', cls: 't-welfare',
    desc: '社會局管理，分「養護型」（生活自理能力缺損、需要照顧）與「安養型」（生活能自理）。' },
  { key: '護理之家', short: '護理之家', icon: 'nursing', cls: 't-nursing',
    desc: '衛生局管理，有護理人員，適合需要鼻胃管、導尿管等護理的長者。' },
  { key: '住宿式長照機構', short: '住宿式長照機構', icon: 'ltc', cls: 't-ltc',
    desc: '長期照顧服務法下的新制機構，衛生局管理，部分也提供日間照顧等服務。' },
];
export const typeOf = (i: Inst) => TYPES.find((t) => t.key === i.category)!;

// ---- 服務類型標籤（對應你截圖中的「需求」篩選）
export function serviceTags(i: Inst): string[] {
  const tags: string[] = [];
  if (i.category === '老人福利機構') {
    if (i.sub_type.includes('養護')) tags.push('養護型');
    if (i.sub_type.includes('安養')) tags.push('安養型');
  } else {
    tags.push('長照型');
  }
  if (/失智/.test(i.target) || /失智/.test(i.extra)) tags.push('失智型');
  return tags;
}

// ---- 評鑑等第顯示：圖示＋文字＋顏色（不單靠顏色）
export type Tone = 'gold' | 'green' | 'blue' | 'orange' | 'red' | 'gray';
export function gradeInfo(i: Inst): { text: string; tone: Tone; icon: string; year: string; rank: number } {
  const g = i.eval_grade;
  const year = i.eval_year && i.eval_year !== '—' ? i.eval_year : '';
  const m: Record<string, [string, Tone, string, number]> = {
    '優': ['優等', 'gold', 'award', 0],
    '甲': ['甲等', 'green', 'badge', 1],
    '合格': ['合格', 'green', 'badge', 1],
    '乙': ['乙等', 'blue', 'ok', 3],
    '丙': ['丙等', 'orange', 'warn', 4],
    '不合格': ['不合格', 'red', 'bad', 5],
    '未評鑑': ['尚未評鑑', 'gray', 'unknown', 8],
    '新設立，尚無評鑑': ['新設立，尚無評鑑', 'gray', 'unknown', 8],
    '無評鑑資料': ['無評鑑資料', 'gray', 'unknown', 9],
  };
  const hit = m[g];
  if (hit) return { text: hit[0], tone: hit[1], icon: hit[2], year, rank: hit[3] };
  // 非標準值（例如「合格(本局辦理)」或待確認）
  return { text: g === '待確認' ? '評鑑待確認' : g, tone: 'gray', icon: 'unknown', year, rank: 7 };
}
export const yearNum = (s: string) => parseInt((s.match(/\d+/) || ['0'])[0], 10);

// ---- 排序：同一單位類型內，先依評鑑等第，再依評鑑年度（新到舊），再依行政區
export function sortByGrade(list: Inst[]): Inst[] {
  return [...list].sort((a, b) => {
    const ga = gradeInfo(a), gb = gradeInfo(b);
    return ga.rank - gb.rank || yearNum(gb.year) - yearNum(ga.year) || a.district.localeCompare(b.district, 'zh-Hant') || a.name.localeCompare(b.name, 'zh-Hant');
  });
}

// ---- 床位與收費的簡短文字
export function bedsText(i: Inst): string {
  if (i.src === 'A') return `核定 ${i.beds_licensed ?? '待確認'} 床` + (i.vacancy != null ? `，目前空位 ${i.vacancy}` : '');
  return `核定 ${i.beds_licensed ?? '待確認'} 床` + (i.beds_open != null ? `，開放 ${i.beds_open} 床` : '');
}
export const FEE_RANGE = '37,500～55,000 元／月（依房型）';
export function feeText(i: Inst): string {
  return i.src === 'A' ? '收費：待確認' : `月費上限 ${FEE_RANGE}`;
}

export const districts = [...new Set(insts.map((i) => i.district))].sort((a, b) => a.localeCompare(b, 'zh-Hant'));
export const countBy = (k: string) => insts.filter((i) => i.category === k).length;

export const BASE = import.meta.env.BASE_URL.replace(/\/$/, '');
export const url = (p: string) => `${BASE}${p}`;

// ---- 手動補充資料（官方網站、粉絲專頁），由 data/manual.json 提供
import manualRaw from '../../data/manual.json';
export const manual = manualRaw as unknown as Record<string, { website?: string; fanpage?: string }>;

// ---- 官方收費上限（衛生局 115/7/8 收費標準表）
import feeRaw from '../../data/fee_caps.json';
export const FEES = feeRaw as any;

// ---- 電話：拆成可點擊的號碼
export function phoneLinks(p: string): { text: string; href: string }[] {
  const m = p.match(/0\d{1,3}-?\d{5,8}(?:#\d+)?/g) || [];
  return m.map((t) => ({ text: t, href: 'tel:' + t.replace(/[^\d+]/g, '') }));
}

// ---- 地圖連結（只放連結，不嵌入地圖）
export const mapUrl = (i: Inst) => 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(i.address);

// ---- 同址或同電話的關聯機構
const normAddr = (s: string) => s.replace(/[\s　]/g, '').replace(/臺/g, '台').replace(/之\d+.*$/, '').replace(/\d+樓.*$/, '').replace(/[0-9]+-[0-9]+樓.*$/, '');
export function relatedOf(i: Inst): Inst[] {
  const ph = new Set(phoneLinks(i.phone).map((x) => x.text));
  const a = normAddr(i.address);
  return insts.filter((o) => o.id !== i.id && (
    (a && normAddr(o.address) === a) || phoneLinks(o.phone).some((x) => ph.has(x.text))
  ));
}
