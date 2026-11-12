/* Kuverenga Lens - syllable breaker
 * Shona: syllables are open (consonant cluster + one vowel), e.g. mangwanani -> ma-ngwa-na-ni
 * English: a rule-of-thumb splitter (VC-CV, V-CV, consonant + "le", silent final e). */
(function (global) {
  'use strict';

  const VOWELS = 'aeiou';
  const isVowel = (ch) => VOWELS.includes(ch);

  function shona(word) {
    const lower = word.toLowerCase();
    const parts = [];
    let start = 0;
    for (let i = 0; i < lower.length; i++) {
      if (isVowel(lower[i])) {
        parts.push(word.slice(start, i + 1));
        start = i + 1;
      }
    }
    if (start < word.length) {
      // trailing consonants (rare in Shona, e.g. loan words) stay with the last syllable
      if (parts.length) parts[parts.length - 1] += word.slice(start);
      else parts.push(word.slice(start));
    }
    return parts;
  }

  const KEEP_TOGETHER = ['ch', 'sh', 'th', 'ph', 'wh', 'gh', 'qu'];
  const STAY_LEFT = ['ck', 'ng', 'nk', 'x'];

  function english(word) {
    const w = word.toLowerCase();
    if (w.length <= 3) return [word];

    // mark vowels; y is a vowel when not first letter; final silent e is not counted
    const v = [];
    for (let i = 0; i < w.length; i++) {
      let isV = isVowel(w[i]) || (w[i] === 'y' && i > 0 && !isVowel(w[i - 1]));
      v.push(isV);
    }
    const last = w.length - 1;
    const endsWithLe = /[^aeiou]le$/.test(w);
    if (w[last] === 'e' && !endsWithLe && !/[aeiou]e$/.test(w) && !/(ee|ye)$/.test(w)) v[last] = false;
    if (/[^aeiou]es$/.test(w) && !/(ses|zes|ches|shes|xes|ces|ges)$/.test(w)) v[last - 1] = false;
    if (/[^aeiouldt]ed$/.test(w)) v[last - 1] = false;

    // vowel groups
    const groups = [];
    for (let i = 0; i < w.length; i++) {
      if (v[i] && (i === 0 || !v[i - 1])) groups.push([i, i]);
      else if (v[i]) groups[groups.length - 1][1] = i;
    }
    if (groups.length <= 1) return [word];

    const cuts = [];
    for (let g = 0; g < groups.length - 1; g++) {
      const a = groups[g][1] + 1;          // first consonant after vowel group
      const b = groups[g + 1][0];          // first vowel of next group
      const cluster = w.slice(a, b);
      let cut;
      if (endsWithLe && g === groups.length - 2) {
        cut = b - 2;                       // ta-ble, lit-tle
        if (cluster.length === 1) cut = a;
      } else if (cluster.length <= 1) {
        cut = a;                           // V-CV: ba-by, o-pen
      } else if (KEEP_TOGETHER.some((d) => cluster.startsWith(d)) && cluster.length === 2) {
        cut = a;                           // tea-cher, mo-ther
      } else if (STAY_LEFT.some((d) => cluster.startsWith(d))) {
        cut = a + (cluster.startsWith('x') ? 1 : 2); // pock-et, sing-er
      } else {
        cut = a + 1;                       // VC-CV: sis-ter, win-ter
      }
      if (cut > 0 && cut < w.length) cuts.push(cut);
    }

    const parts = [];
    let prev = 0;
    for (const c of cuts) {
      if (c > prev) { parts.push(word.slice(prev, c)); prev = c; }
    }
    parts.push(word.slice(prev));
    return parts.filter(Boolean);
  }

  function split(word, lang) {
    if (!/^[A-Za-z']+$/.test(word)) return [word];
    return lang === 'sn' ? shona(word) : english(word);
  }

  global.Syllables = { split, shona, english };
})(window);
