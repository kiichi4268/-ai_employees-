// オリジナルのマスコットを SVG で描く（ポーズ・表情を変えられる）
function mascot({pose='point', face='smile', text='', w=370, h=320, bg=null}){
  const B='#5b8fd6',BD='#3f6fb8',O='#f2794a',OD='#d95f33',G='#8d96a3',INK='#1d2433';
  const eyes = face==='wink'
    ? `<ellipse cx="262" cy="250" rx="13" ry="17" fill="${INK}"/><circle cx="266" cy="243" r="5" fill="#fff"/><path d="M325 252 q13 -12 26 0" stroke="${INK}" stroke-width="7" fill="none" stroke-linecap="round"/>`
    : face==='wow'
    ? `<ellipse cx="262" cy="248" rx="14" ry="19" fill="${INK}"/><ellipse cx="338" cy="248" rx="14" ry="19" fill="${INK}"/><circle cx="266" cy="241" r="5" fill="#fff"/><circle cx="342" cy="241" r="5" fill="#fff"/>`
    : face==='happy'
    ? `<path d="M248 252 q14 -16 28 0" stroke="${INK}" stroke-width="7" fill="none" stroke-linecap="round"/><path d="M324 252 q14 -16 28 0" stroke="${INK}" stroke-width="7" fill="none" stroke-linecap="round"/>`
    : `<ellipse cx="262" cy="250" rx="13" ry="17" fill="${INK}"/><ellipse cx="338" cy="250" rx="13" ry="17" fill="${INK}"/><circle cx="266" cy="243" r="5" fill="#fff"/><circle cx="342" cy="243" r="5" fill="#fff"/>`;
  const mouth = face==='wow' ? `<ellipse cx="300" cy="292" rx="11" ry="13" fill="${INK}"/>`
    : face==='happy' ? `<path d="M276 282 q24 30 48 0 z" fill="${INK}"/><path d="M286 292 q14 10 28 0" fill="#e86a7a"/>`
    : `<path d="M280 284 q20 18 40 0" stroke="${INK}" stroke-width="6" fill="none" stroke-linecap="round"/>`;
  const sweat = face==='sweat' ? `<path d="M392 210 q12 18 0 28 q-12 -10 0 -28z" fill="#9fd3ff" stroke="${BD}" stroke-width="3"/>` : '';
  const armL = pose==='yay' ? `<path d="M210 395 q-50 -40 -70 -100" stroke="${O}" stroke-width="46" stroke-linecap="round" fill="none"/><circle cx="138" cy="285" r="24" fill="${B}" stroke="${BD}" stroke-width="4"/>`
    : `<path d="M205 400 q-30 40 -30 85" stroke="${O}" stroke-width="46" stroke-linecap="round" fill="none"/><circle cx="175" cy="500" r="23" fill="${B}" stroke="${BD}" stroke-width="4"/>`;
  const armR = pose==='point'
    ? `<path d="M395 400 q50 -20 70 -80" stroke="${O}" stroke-width="46" stroke-linecap="round" fill="none"/><circle cx="470" cy="305" r="24" fill="${B}" stroke="${BD}" stroke-width="4"/><rect x="474" y="262" width="16" height="44" rx="8" fill="${B}" stroke="${BD}" stroke-width="4" transform="rotate(25 482 284)"/>`
    : pose==='yay'
    ? `<path d="M390 395 q50 -40 70 -100" stroke="${O}" stroke-width="46" stroke-linecap="round" fill="none"/><circle cx="462" cy="285" r="24" fill="${B}" stroke="${BD}" stroke-width="4"/>`
    : `<path d="M395 400 q55 -10 75 -75" stroke="${O}" stroke-width="46" stroke-linecap="round" fill="none"/><g transform="rotate(-15 476 300)"><rect x="452" y="270" width="48" height="50" rx="20" fill="${B}" stroke="${BD}" stroke-width="4"/><path d="M462 272 v-18 M476 270 v-22 M490 272 v-18" stroke="${BD}" stroke-width="12" stroke-linecap="round"/><path d="M462 272 v-18 M476 270 v-22 M490 272 v-18" stroke="${B}" stroke-width="6" stroke-linecap="round"/></g>`;
  const label = text ? `<text x="300" y="${text.length>6?672:678}" text-anchor="middle" font-family="Noto Sans CJK JP, sans-serif" font-weight="900" font-size="${text.length>6?64:76}" fill="#fff" stroke="${INK}" stroke-width="14" stroke-linejoin="round" paint-order="stroke">${text}</text>` : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 ${text?-10:0} 600 ${text?720:620}" width="${w}" height="${h}">
  ${bg?`<rect y="-10" width="600" height="730" fill="${bg}"/>`:''}
  <ellipse cx="300" cy="575" rx="120" ry="14" fill="#00000018"/>
  <rect x="245" y="500" width="40" height="55" fill="${B}"/><rect x="315" y="500" width="40" height="55" fill="${B}"/>
  <path d="M225 545 h65 q8 0 8 10 v6 h-80 q-6 -16 7 -16z" fill="#3a63a8"/><path d="M310 545 h65 q13 0 7 16 h-80 v-6 q0 -10 8 -10z" fill="#3a63a8"/>
  <rect x="222" y="557" width="78" height="9" rx="4" fill="#fff"/><rect x="302" y="557" width="78" height="9" rx="4" fill="#fff"/>
  <path d="M225 470 h150 l8 50 h-75 l-8 -14 l-8 14 h-75z" fill="${G}"/>
  ${armL}
  <path d="M200 360 q0 -30 40 -40 h120 q40 10 40 40 l10 120 q0 18 -20 18 h-180 q-20 0 -20 -18z" fill="${O}" stroke="${OD}" stroke-width="5"/>
  <rect x="250" y="430" width="100" height="44" rx="14" fill="${OD}" opacity=".35"/>
  <text x="300" y="418" text-anchor="middle" font-family="Noto Sans CJK JP, sans-serif" font-weight="900" font-size="50" fill="#fff">M</text>
  <path d="M286 345 v38 M314 345 v38" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
  ${armR}
  <ellipse cx="300" cy="335" rx="150" ry="62" fill="${O}" stroke="${OD}" stroke-width="5"/>
  <circle cx="300" cy="250" r="125" fill="${B}" stroke="${BD}" stroke-width="5"/>
  <clipPath id="hc"><circle cx="300" cy="250" r="123"/></clipPath>
  <g clip-path="url(#hc)"><path d="M160 205 Q300 150 440 205" stroke="#fff" stroke-width="40" fill="none"/><path d="M160 200 Q300 145 440 200" stroke="#e5484d" stroke-width="13" fill="none"/><path d="M160 216 Q300 161 440 216" stroke="#2f5fb3" stroke-width="5" fill="none"/></g>
  
  ${eyes}<ellipse cx="236" cy="282" rx="17" ry="11" fill="#f19aa8" opacity=".8"/><ellipse cx="364" cy="282" rx="17" ry="11" fill="#f19aa8" opacity=".8"/>
  ${mouth}${sweat}${label}</svg>`;
}
module.exports={mascot};
