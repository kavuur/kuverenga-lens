/* Kuverenga Lens - main app
 * SNAP (camera / photo) -> CONVERT (clean image + on-device OCR) -> READ (dyslexia-friendly view + read aloud) */
(function () {
  'use strict';

  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  /* ---------------- Text in two languages ---------------- */
  const STRINGS = {
    en: {
      heroTitle: 'Read the board your way',
      heroText: 'Take a photo of the chalkboard. Kuverenga Lens turns it into clear text and reads it to you.',
      snap: 'Snap', snapHint: 'Photo of the board',
      convert: 'Convert', convertHint: 'Photo to clear text',
      read: 'Read', readHint: 'See it and hear it',
      snapBoard: 'Snap the board', upload: 'Choose a photo', typeText: 'Type or paste',
      install: 'Install on this phone', recent: 'Recent notes',
      cleanTitle: 'Clean the photo', boardMode: 'Chalkboard (light writing on dark board)',
      contrast: 'Contrast', bw: 'Sharp black & white', rotate: 'Rotate', retake: 'Retake',
      convertBtn: 'Convert to text',
      listen: 'Listen', pause: 'Pause', syllables: 'Syllables', display: 'Display',
      font: 'Font', size: 'Text size', spacing: 'Line spacing', background: 'Background',
      speed: 'Reading speed', focus: 'Focus line (dim other sentences)',
      tapHint: 'Tip: tap any word to hear it on its own.',
      unsure: 'Check this word', unsureNote: 'Words with a wavy line may be wrong. Tap Fix text to correct them.', textLang: 'Text language:',
      fix: 'Fix text', save: 'Save note', fixTitle: 'Fix or type the text',
      fixHint: 'Correct any words the camera read wrongly, then tap Done.',
      cancel: 'Cancel', done: 'Done', myNotes: 'My notes',
      noNotes: 'No saved notes yet. Snap the board to make your first one.',
      home: 'Home', notes: 'Notes', help: 'Help',
      h1: 'Getting a good photo',
      h1a: 'Stand straight in front of the board, not at an angle.',
      h1b: 'Fill the screen with the part you want to read.',
      h1c: 'Avoid glare from windows. Hold the phone still.',
      h1d: 'Clear, neat printing works best. Joined handwriting may need fixing.',
      h2: 'Reading tools',
      h2a: 'OpenDyslexic font has heavy letter bottoms so b and d do not flip.',
      h2b: 'Syllables splits long words into small parts: ma·ngwa·na·ni.',
      h2c: 'Change the background colour until reading feels comfortable.',
      h2d: 'Listen reads the text aloud and highlights each sentence.',
      h3: 'Privacy',
      h3a: 'Everything happens on this phone. Photos and notes are never uploaded.',
      langName: { en: 'English', sn: 'ChiShona' },
      stLoading: 'Getting the reader ready…', stReading: 'Reading the board…', stDone: 'Done!',
      engine: 'Reading engine', engFast: 'Fast', engFastHint: 'print & neat writing', engHand: 'Handwriting', engHandHint: 'better for chalk handwriting',
      handNote: 'Handwriting mode downloads a 75 MB reader once (use Wi-Fi). After that it works offline.',
      stHandDl: 'Downloading the handwriting reader (one time only)…', stHandLine: 'Reading line', stOf: 'of',
      handFail: 'The handwriting reader needs internet the first time. Connect and try again, or use Fast.',
      stFirst: 'First time only: loading the reading engine…',
      noText: 'No words found. Try a closer, straighter photo, or switch Chalkboard mode.',
      saved: 'Note saved', deleted: 'Note deleted', noVoice: 'This phone has no voice for reading aloud.',
      voiceUsing: 'Voice: ', voiceFallbackSn: 'No ChiShona voice on this phone, so a similar voice is used. Install a Shona or Swahili voice in phone Settings › Text-to-speech for better sound.',
      ocrFail: 'Sorry, the photo could not be read. Please try again.',
      untitled: 'Board note', deleteQ: 'Delete this note?',
      iosInstall: 'On iPhone: tap Share, then “Add to Home Screen”.',
      fileTitle: 'Open the app from its web link',
      fileMode: 'The app was opened as a file, so the phone blocks the reading engine. Open it from its web link (https://…) instead.'
    },
    sn: {
      heroTitle: 'Verenga bhodhi nenzira yako',
      heroText: 'Tora mufananidzo webhodhi. Kuverenga Lens inoushandura kuita mavara akajeka uye inokuverengera.',
      snap: 'Tora', snapHint: 'Mufananidzo webhodhi',
      convert: 'Shandura', convertHint: 'Mufananidzo kuita mavara',
      read: 'Verenga', readHint: 'Ona uye unzwe',
      snapBoard: 'Tora mufananidzo webhodhi', upload: 'Sarudza mufananidzo', typeText: 'Nyora kana isa',
      install: 'Isa pafoni iyi', recent: 'Zvinyorwa zvichangobva',
      cleanTitle: 'Chenesa mufananidzo', boardMode: 'Bhodhi (choko chena pabhodhi dema)',
      contrast: 'Kujeka', bw: 'Dema nechena chete', rotate: 'Tenderedza', retake: 'Tora zvakare',
      convertBtn: 'Shandura kuita mavara',
      listen: 'Teerera', pause: 'Mira', syllables: 'Zvikamu', display: 'Kuratidza',
      font: 'Mavara', size: 'Ukuru hwemavara', spacing: 'Nzvimbo pakati pemitsara', background: 'Ruvara rwepasi',
      speed: 'Kumhanya kwekuverenga', focus: 'Tarisa mutsara (dzima mimwe mitsara)',
      tapHint: 'Bata shoko ripi neripi kuti urinzwe roga.',
      unsure: 'Tarisa shoko iri', unsureNote: 'Mashoko ane mutsara unokombama angave asina kunaka. Bata Gadzirisa kuti uagadzirise.', textLang: 'Mutauro wemavara:',
      fix: 'Gadzirisa', save: 'Chengetedza', fixTitle: 'Gadzirisa kana nyora mavara',
      fixHint: 'Gadzirisa mashoko akaverengwa zvisizvo, wobva wabata Zvapera.',
      cancel: 'Kanzura', done: 'Zvapera', myNotes: 'Zvinyorwa zvangu',
      noNotes: 'Hapana zvinyorwa zvakachengetedzwa. Tora mufananidzo webhodhi kuti utange.',
      home: 'Kumba', notes: 'Zvinyorwa', help: 'Rubatsiro',
      h1: 'Kutora mufananidzo wakanaka',
      h1a: 'Mira wakatarisana nebhodhi, kwete wakatsveyama.',
      h1b: 'Zadza skrini nechikamu chaunoda kuverenga.',
      h1c: 'Dzivisa kupenya kwezuva kubva pamahwindo. Bata foni yakadzikama.',
      h1d: 'Mavara akanyorwa zvakajeka anoshanda zvakanyanya. Mavara akabatanidzwa anogona kuda kugadziriswa.',
      h2: 'Zvishandiso zvekuverenga',
      h2a: 'Mavara eOpenDyslexic ane pasi rakarema kuti b na d zvisachinjane.',
      h2b: 'Zvikamu zvinopatsanura mashoko marefu: ma·ngwa·na·ni.',
      h2c: 'Chinja ruvara rwepasi kusvikira kuverenga kwanyanya kureruka.',
      h2d: 'Teerera inoverenga mavara zvinonzwika uye inoratidza mutsara wega wega.',
      h3: 'Kuvanzika',
      h3a: 'Zvese zvinoitika pafoni iyi. Mifananidzo nezvinyorwa hazvitumirwe kupi zvako.',
      langName: { en: 'ChiRungu', sn: 'ChiShona' },
      stLoading: 'Kugadzirira…', stReading: 'Kuverenga bhodhi…', stDone: 'Zvapera!',
      engine: 'Injini yekuverenga', engFast: 'Nekukurumidza', engFastHint: 'mavara akadhindwa', engHand: 'Manyorerwo', engHandHint: 'zvirinani pamanyorerwo echoko',
      handNote: 'Manyorerwo anorodha 75 MB kamwe chete (shandisa Wi-Fi). Mushure maizvozvo anoshanda pasina internet.',
      stHandDl: 'Kurodha injini yemanyorerwo (kamwe chete)…', stHandLine: 'Kuverenga mutsara', stOf: 'pa',
      handFail: 'Injini yemanyorerwo inoda internet kekutanga. Batana wozoedza zvakare, kana shandisa Nekukurumidza.',
      stFirst: 'Kekutanga chete: kurodha injini yekuverenga…',
      noText: 'Hapana mashoko awanikwa. Edza mufananidzo wepedyo, wakatwasuka.',
      saved: 'Chinyorwa chachengetedzwa', deleted: 'Chinyorwa chadzimwa', noVoice: 'Foni iyi haina izwi rekuverenga.',
      voiceUsing: 'Izwi: ', voiceFallbackSn: 'Foni iyi haina izwi reChiShona, saka izwi rakafanana rinoshandiswa. Isa izwi reShona kana Swahili muSettings › Text-to-speech.',
      ocrFail: 'Ndine urombo, mufananidzo hauna kuverengeka. Edza zvakare.',
      untitled: 'Chinyorwa chebhodhi', deleteQ: 'Dzima chinyorwa ichi?',
      iosInstall: 'PaiPhone: bata Share, wobva wasarudza “Add to Home Screen”.',
      fileTitle: 'Vhura app kubva pa link yayo',
      fileMode: 'App yavhurwa sefaira, saka foni inovharira injini yekuverenga. Ivhure kubva pa link yayo (https://…).'
    }
  };

  /* ---------------- Settings (remembered on the phone) ---------------- */
  const DEFAULTS = { engine: 'fast', ui: 'en', font: 'dyslexic', size: 24, spacing: 2, bg: 'cream', rate: 0.85, syll: false, focus: false };
  const BG = {
    cream: ['#FFF6DC', '#1B1B1B'], blue: ['#DCEBFA', '#1B1B1B'], green: ['#DFF2E1', '#1B1B1B'],
    peach: ['#FBE3D3', '#1B1B1B'], yellow: ['#FFF3A8', '#1B1B1B'], dark: ['#20262B', '#F3EEDF']
  };

  function load(key, fallback) {
    try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
  }
  function store(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* storage unavailable */ }
  }

  const settings = Object.assign({}, DEFAULTS, load('kl.settings', {}));
  const t = (k) => (STRINGS[settings.ui] && STRINGS[settings.ui][k]) || STRINGS.en[k] || k;

  /* ---------------- State ---------------- */
  const state = {
    source: null,       // canvas with the original (rotated) photo
    text: '',
    textLang: 'en',
    noteId: null,
    unsure: new Set(),  // words the camera was not sure about
    sentences: [],      // [{el, text, words:[{el,start,end,text}]}]
    playing: false,
    sentIdx: 0,
    worker: null,
    hand: null,         // handwriting reader (loaded on first use)
    installEvt: null
  };

  /* ---------------- Navigation ---------------- */
  function show(name) {
    $$('.screen').forEach((s) => s.classList.toggle('active', s.id === 'screen-' + name));
    $$('.tabbar button').forEach((b) => b.classList.toggle('on', b.dataset.go === name));
    if (name !== 'reader') stopSpeech();
    if (name === 'notes') renderNotes();
    if (name === 'home') renderRecent();
    window.scrollTo(0, 0);
  }
  $$('.tabbar button').forEach((b) => b.addEventListener('click', () => show(b.dataset.go)));

  function toast(msg, ms) {
    const el = $('#toast');
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => el.classList.remove('show'), ms || 2600);
  }

  /* ---------------- Language ---------------- */
  function applyUiLang() {
    document.documentElement.lang = settings.ui;
    $$('[data-i18n]').forEach((el) => { el.textContent = t(el.dataset.i18n); });
    $$('.lang-switch button').forEach((b) => b.classList.toggle('on', b.dataset.lang === settings.ui));
    updateTextLangChip();
    updatePlayButton();
  }
  $$('.lang-switch button').forEach((b) => b.addEventListener('click', () => {
    settings.ui = b.dataset.lang;
    store('kl.settings', settings);
    applyUiLang();
    if (!state.noteId && !state.text) state.textLang = settings.ui;
    renderNotes(); renderRecent();
  }));

  const EN_COMMON = new Set(('the and is are was were of to in on for with this that it a an we you they he she ' +
    'what which how why when where be have has had do does did not can will our your their from by as at or ' +
    'there these those plants water sun').split(' '));
  function detectLang(text) {
    const words = (text.toLowerCase().match(/[a-z']+/g) || []);
    if (!words.length) return settings.ui;
    const en = words.filter((w) => EN_COMMON.has(w)).length / words.length;
    const open = words.filter((w) => /[aeiou]$/.test(w)).length / words.length;
    const shonaBits = words.filter((w) => /(zv|sv|dz|ng'|^ku|^chi|^mu|^va|^zvi|mhu|nhu|bh|dh|vh)/.test(w)).length / words.length;
    if (en > 0.12) return 'en';
    if (open > 0.72 || shonaBits > 0.25) return 'sn';
    return 'en';
  }
  function updateTextLangChip() {
    const chip = $('#btn-textlang');
    if (chip) chip.textContent = t('langName')[state.textLang] + ' ⇄';
  }
  $('#btn-textlang').addEventListener('click', () => {
    stopSpeech();
    state.textLang = state.textLang === 'en' ? 'sn' : 'en';
    updateTextLangChip();
    renderReader();
    updateVoiceNote();
  });

  /* ---------------- SNAP: load a photo ---------------- */
  const MAX_SIDE = 1800;

  async function loadFile(file) {
    if (!file) return;
    let bmp;
    try {
      bmp = await createImageBitmap(file, { imageOrientation: 'from-image' });
    } catch (e) {
      bmp = await new Promise((res, rej) => {
        const img = new Image();
        img.onload = () => res(img);
        img.onerror = rej;
        img.src = URL.createObjectURL(file);
      });
    }
    const w = bmp.width, h = bmp.height;
    const scale = Math.min(1, MAX_SIDE / Math.max(w, h));
    const c = document.createElement('canvas');
    c.width = Math.round(w * scale);
    c.height = Math.round(h * scale);
    c.getContext('2d').drawImage(bmp, 0, 0, c.width, c.height);
    state.source = c;
    $('#opt-board').checked = meanLuma(c) < 120;   // dark board -> light chalk writing
    show('review');
    processPreview();
  }
  $('#camera-input').addEventListener('change', (e) => { loadFile(e.target.files[0]); e.target.value = ''; });
  $('#upload-input').addEventListener('change', (e) => { loadFile(e.target.files[0]); e.target.value = ''; });
  $('#btn-retake').addEventListener('click', () => $('#camera-input').click());

  function meanLuma(canvas) {
    const small = document.createElement('canvas');
    small.width = 64; small.height = Math.max(1, Math.round(64 * canvas.height / canvas.width));
    const g = small.getContext('2d');
    g.drawImage(canvas, 0, 0, small.width, small.height);
    const d = g.getImageData(0, 0, small.width, small.height).data;
    let sum = 0;
    for (let i = 0; i < d.length; i += 4) sum += 0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2];
    return sum / (d.length / 4);
  }

  $('#btn-rotate').addEventListener('click', () => {
    const s = state.source; if (!s) return;
    const c = document.createElement('canvas');
    c.width = s.height; c.height = s.width;
    const g = c.getContext('2d');
    g.translate(c.width, 0); g.rotate(Math.PI / 2); g.drawImage(s, 0, 0);
    state.source = c;
    processPreview();
  });
  ['#opt-board', '#opt-contrast', '#opt-bw'].forEach((id) => $(id).addEventListener('input', processPreview));

  /* ---------------- CONVERT: clean the image ---------------- */
  // v3 (after testing on a real classroom photo):
  //  1. grey: darkest colour channel for a chalkboard (chalk is bright in every channel, the board is not)
  //  2. top-hat: keep only thin strokes, which removes wipe-smears, dust haze and glare (all wide areas)
  //  3. threshold to ink / no ink
  //  4. remove underlines, divider lines, the board edge and specks; keep dashes and dots that sit next to words
  //  5. dark ink on a white page, slightly softened, which suits the OCR engine
  // v1 (contrast stretch) and v2 (background flattening) read only ~5% of a real chalk board; v3 reads ~55-60%.
  function minMaxFilter(src, W, H, r, useMax) {
    // separable square min/max filter of radius r
    const tmp = new Float32Array(W * H), out = new Float32Array(W * H);
    for (let y = 0; y < H; y++) {
      const row = y * W;
      for (let x = 0; x < W; x++) {
        let v = src[row + x];
        const x0 = Math.max(0, x - r), x1 = Math.min(W - 1, x + r);
        for (let k = x0; k <= x1; k++) { const s = src[row + k]; if (useMax ? s > v : s < v) v = s; }
        tmp[row + x] = v;
      }
    }
    for (let x = 0; x < W; x++) {
      for (let y = 0; y < H; y++) {
        let v = tmp[y * W + x];
        const y0 = Math.max(0, y - r), y1 = Math.min(H - 1, y + r);
        for (let k = y0; k <= y1; k++) { const s = tmp[k * W + x]; if (useMax ? s > v : s < v) v = s; }
        out[y * W + x] = v;
      }
    }
    return out;
  }

  function labelComponents(mask, W, H) {
    // 8-connected labelling; returns labels and per-component box + pixel count
    const labels = new Int32Array(W * H);
    const comps = [null];
    const stack = new Int32Array(W * H);
    for (let start = 0; start < W * H; start++) {
      if (!mask[start] || labels[start]) continue;
      const id = comps.length;
      const c = { x0: W, y0: H, x1: 0, y1: 0, n: 0 };
      let sp = 0; stack[sp++] = start; labels[start] = id;
      while (sp) {
        const p = stack[--sp], x = p % W, y = (p - x) / W;
        c.n++; if (x < c.x0) c.x0 = x; if (x > c.x1) c.x1 = x; if (y < c.y0) c.y0 = y; if (y > c.y1) c.y1 = y;
        for (let dy = -1; dy <= 1; dy++) {
          const yy = y + dy; if (yy < 0 || yy >= H) continue;
          for (let dx = -1; dx <= 1; dx++) {
            const xx = x + dx; if (xx < 0 || xx >= W) continue;
            const q = yy * W + xx;
            if (mask[q] && !labels[q]) { labels[q] = id; stack[sp++] = q; }
          }
        }
      }
      comps.push(c);
    }
    return { labels, comps };
  }

  function cleanImage(src, opts) {
    const W = src.width, H = src.height, n = W * H;
    const c = document.createElement('canvas');
    c.width = W; c.height = H;
    const g = c.getContext('2d', { willReadFrequently: true });
    g.drawImage(src, 0, 0);
    const img = g.getImageData(0, 0, W, H);
    const d = img.data;

    // 1. grey; flip a light page so the writing is always the bright part
    const grey = new Float32Array(n);
    for (let i = 0, p = 0; p < n; i += 4, p++) {
      grey[p] = opts.board ? Math.min(d[i], d[i + 1], d[i + 2]) : 255 - (0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]);
    }
    // 2. top-hat = image - opening(image): only strokes thinner than the filter survive
    const r = Math.max(2, Math.round(8 * W / 1800));
    const opened = minMaxFilter(minMaxFilter(grey, W, H, r, false), W, H, r, true);
    const hist = new Uint32Array(256);
    const th = new Float32Array(n);
    for (let p = 0; p < n; p++) { th[p] = Math.max(0, grey[p] - opened[p]); hist[Math.min(255, (th[p] * 2) | 0)]++; }
    // 3. threshold (Otsu); the Contrast slider makes faint chalk count more (higher) or less (lower)
    const sensitivity = 1.75 - opts.contrast / 100;          // default 75 -> 1.0
    const thr = Math.max(12, otsu(hist, n) / 2) * sensitivity;
    const mask = new Uint8Array(n);
    for (let p = 0; p < n; p++) mask[p] = th[p] > thr ? 1 : 0;

    // 4. remove lines, frame and specks
    const { labels, comps } = labelComponents(mask, W, H);
    const keep = new Uint8Array(comps.length);
    const dividers = [];
    const bigSize = 0.00012 * n, speck = 0.00002 * n;
    for (let id = 1; id < comps.length; id++) {
      const k = comps[id], w = k.x1 - k.x0 + 1, h = k.y1 - k.y0 + 1;
      if (k.n < speck) continue;
      if (w > 0.12 * W && h < 0.06 * H) continue;             // underline / horizontal rule
      if (h > 0.30 * H && w < 0.04 * W) { dividers.push({ x: (k.x0 + k.x1) / 2, y0: k.y0, y1: k.y1 }); continue; }   // column divider
      if (h > 0.5 * H || w > 0.6 * W) continue;               // board frame or big blotch
      if (k.x0 === 0 || k.y0 === 0 || k.x1 === W - 1 || k.y1 === H - 1) continue;   // touches photo edge
      keep[id] = k.n >= bigSize ? 2 : 1;                       // 2 = letter-sized, 1 = small mark
    }
    // small marks stay only near a letter-sized mark (dashes, dots on i)
    const big = new Float32Array(n);
    for (let p = 0; p < n; p++) big[p] = keep[labels[p]] === 2 ? 1 : 0;
    const near = minMaxFilter(big, W, H, Math.max(4, Math.round(W / 120)), true);
    for (let p = 0; p < n; p++) {
      const k = keep[labels[p]];
      mask[p] = k === 2 || (k === 1 && near[p] > 0) ? 1 : 0;
    }
    // 5. dark ink on white
    for (let i = 0, p = 0; p < n; i += 4, p++) {
      const v = mask[p] ? 0 : 255;
      d[i] = d[i + 1] = d[i + 2] = v; d[i + 3] = 255;
    }
    g.putImageData(img, 0, 0);
    c.layout = { dividers };
    if (opts.bw) return c;
    // soften stroke edges slightly (the OCR engine was trained on smooth printed letters)
    const soft = document.createElement('canvas');
    soft.width = W; soft.height = H;
    const sg = soft.getContext('2d');
    sg.fillStyle = '#fff'; sg.fillRect(0, 0, W, H);
    sg.filter = 'blur(0.8px)';
    sg.drawImage(c, 0, 0);
    soft.layout = { dividers };
    return soft;
  }

  function otsu(hist, total) {
    let sum = 0;
    for (let i = 0; i < 256; i++) sum += i * hist[i];
    let sumB = 0, wB = 0, best = 0, thr = 127;
    for (let i = 0; i < 256; i++) {
      wB += hist[i]; if (!wB) continue;
      const wF = total - wB; if (!wF) break;
      sumB += i * hist[i];
      const mB = sumB / wB, mF = (sum - sumB) / wF;
      const between = wB * wF * (mB - mF) * (mB - mF);
      if (between > best) { best = between; thr = i; }
    }
    return thr;
  }

  function currentOpts() {
    return { board: $('#opt-board').checked, contrast: +$('#opt-contrast').value, bw: $('#opt-bw').checked };
  }

  let previewRaf = 0;
  function processPreview() {
    cancelAnimationFrame(previewRaf);
    previewRaf = requestAnimationFrame(() => {
      if (!state.source) return;
      const cleaned = cleanImage(state.source, currentOpts());
      const pc = $('#preview-canvas');
      pc.width = cleaned.width; pc.height = cleaned.height;
      pc.getContext('2d').drawImage(cleaned, 0, 0);
    });
  }

  /* ---------------- CONVERT: on-device OCR (Tesseract.js) ---------------- */
  const STATUS = {
    'loading tesseract core': 'stFirst', 'initializing tesseract': 'stLoading',
    'loading language traineddata': 'stFirst', 'initializing api': 'stLoading',
    'recognizing text': 'stReading'
  };

  function setProgress(p, msgKey) {
    $('#ocr-progress').hidden = false;
    $('#ocr-bar').style.width = Math.round(p * 100) + '%';
    if (msgKey) $('#ocr-status').textContent = t(msgKey);
  }

  async function getWorker() {
    if (state.worker) return state.worker;
    const worker = await Tesseract.createWorker('eng', 1, {
      // absolute URLs: the worker resolves paths relative to itself, not the page
      workerPath: new URL('vendor/tesseract/worker.min.js', location.href).href,
      corePath: new URL('vendor/tesseract', location.href).href,
      langPath: new URL('vendor/lang', location.href).href,
      workerBlobURL: false,
      logger: (m) => {
        const key = STATUS[m.status];
        const base = m.status === 'recognizing text' ? 0.3 : 0;
        const span = m.status === 'recognizing text' ? 0.7 : 0.3;
        setProgress(base + span * (m.progress || 0), key);
      }
    });
    await worker.setParameters({ preserve_interword_spaces: '1' });
    state.worker = worker;   // keep only a worker that started fully
    return worker;
  }

  // Build clean text from Tesseract lines. Judged word by word (v3): stray marks and tiny low-confidence
  // fragments are dropped; a line is kept if it has at least one confident real word.
  function linesFromOcr(data) {
    const lines = [];
    (data.blocks || []).forEach((b) => (b.paragraphs || []).forEach((p) => (p.lines || []).forEach((l) => {
      const words = [];
      (l.words || []).forEach((w) => {
        const text = w.text.replace(/[|_~`^<>{}\[\]\\"“”‘’¢©®]+/g, '').trim();
        const letters = text.replace(/[^A-Za-z0-9]/g, '').length;
        if (!text) return;
        if (letters === 0 && text !== '-' && text !== '–') return;   // stray punctuation
        if (w.confidence < 35 && letters <= 2) return;                // tiny unsure fragment
        if (w.confidence < 20) return;                                // almost certainly noise
        words.push({ text, conf: w.confidence });
      });
      if (!words.some((w) => w.text.replace(/[^A-Za-z0-9]/g, '').length >= 3 && w.conf >= 50)) return;
      lines.push(words);
    })));
    return lines;
  }

  // Board lines wrap at the edge of the board: join a line to the next when the sentence clearly continues
  function joinLines(lines) {
    const out = [];
    lines.forEach((line) => {
      const text = line.join(' ');
      const prev = out[out.length - 1];
      if (prev && !/[.!?:;]$/.test(prev) && /^[a-z]/.test(text)) out[out.length - 1] = prev + ' ' + text;
      else out.push(text);
    });
    return out.join('\n');
  }

  /* ---------------- CONVERT: handwriting engine (TrOCR, optional) ----------------
   * Tesseract is built for print and reads chalk handwriting poorly. TrOCR (trained on handwriting) reads it far
   * better but needs a one-time ~75 MB download, so it is optional. The model is cached by the browser and the
   * service worker, so after the first use it works offline. Runs on the phone through transformers.js (WebAssembly). */
  const TRANSFORMERS_URL = 'https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.2/dist/transformers.min.js';
  const HAND_MODEL = 'Xenova/trocr-small-handwritten';

  async function getHandReader() {
    if (state.hand) return state.hand;
    const tf = await import(TRANSFORMERS_URL);
    tf.env.allowLocalModels = false;
    tf.env.useBrowserCache = true;
    const files = {};
    const reader = await tf.pipeline('image-to-text', HAND_MODEL, {
      dtype: 'q8', device: 'wasm',
      progress_callback: (e) => {
        if (e.status === 'progress' && e.total) {
          files[e.file] = [e.loaded, e.total];
          const all = Object.values(files), done = all.reduce((a, f) => a + f[0], 0), tot = all.reduce((a, f) => a + f[1], 0);
          setProgress(0.05 + 0.45 * (done / tot), 'stHandDl');
        }
      }
    });
    state.hand = reader;
    return reader;
  }

  // Cut the cleaned board into one image per written line. Where a divider line runs down the board, the two
  // sides are read as separate columns (left column first). Big gaps inside a line split it into pieces.
  function segmentLines(cleaned) {
    const W = cleaned.width, H = cleaned.height;
    const px = cleaned.getContext('2d').getImageData(0, 0, W, H).data;
    const ink = new Uint8Array(W * H);
    for (let p = 0, i = 0; p < W * H; p++, i += 4) ink[p] = px[i] < 160 ? 1 : 0;
    const dv = (cleaned.layout && cleaned.layout.dividers) || [];
    let regions = [[0, W, 0, H]];
    if (dv.length) {
      const d = dv.reduce((a, b) => (b.y1 - b.y0 > a.y1 - a.y0 ? b : a));
      const x = Math.round(d.x);
      regions = [[0, W, 0, d.y0], [0, x, d.y0, d.y1 + 1], [x, W, d.y0, d.y1 + 1], [0, W, d.y1 + 1, H]];
    }
    const pieces = [];
    regions.forEach(([x0, x1, y0, y1]) => {
      if (y1 - y0 < 0.02 * H || x1 - x0 < 0.05 * W) return;
      // smoothed row profile -> bands of writing
      const prof = new Float32Array(y1 - y0);
      for (let y = y0; y < y1; y++) { let n = 0; for (let x = x0; x < x1; x++) n += ink[y * W + x]; prof[y - y0] = n; }
      const sm = new Float32Array(prof.length);
      for (let i = 0; i < prof.length; i++) { let a = 0, c = 0; for (let k = -6; k <= 6; k++) { const j = i + k; if (j >= 0 && j < prof.length) { a += prof[j]; c++; } } sm[i] = a / c; }
      let mx = 0; sm.forEach((v) => { if (v > mx) mx = v; });
      const on = Array.from(sm, (v) => v > Math.max(3, 0.12 * mx));
      let bands = [];
      for (let i = 0; i < on.length; i++) {
        if (on[i] && (i === 0 || !on[i - 1])) bands.push([i, i]);
        else if (on[i]) bands[bands.length - 1][1] = i;
      }
      bands = bands.filter((b) => b[1] - b[0] > 0.02 * H);
      if (!bands.length) return;
      const hs = bands.map((b) => b[1] - b[0]).sort((a, b) => a - b), med = hs[hs.length >> 1];
      const split = [];
      bands.forEach(([a, b]) => {
        while (b - a > 1.6 * med) {               // two lines touching: cut at the emptiest row
          const lo = a + Math.round(0.35 * med), hi = b - Math.round(0.35 * med);
          let cut = lo; for (let i = lo; i < hi; i++) if (sm[i] < sm[cut]) cut = i;
          split.push([a, cut]); a = cut;
        }
        split.push([a, b]);
      });
      split.forEach(([a, b]) => {
        if (b - a < 0.45 * med) return;           // sliver between lines
        const ya = y0 + a, yb = y0 + b, lh = yb - ya;
        // column profile inside the band -> runs of ink ("segments"), then pieces separated by big gaps
        const colInk = new Uint32Array(x1 - x0);
        for (let x = x0; x < x1; x++) { let n = 0; for (let y = ya; y <= yb; y++) n += ink[y * W + x]; colInk[x - x0] = n; }
        const segs = [];
        let s0 = -1, last = -1;
        for (let i = 0; i < colInk.length; i++) {
          if (!colInk[i]) continue;
          if (s0 >= 0 && i - last > 0.15 * lh) { segs.push([s0, last]); s0 = -1; }
          if (s0 < 0) s0 = i;
          last = i;
        }
        if (s0 >= 0) segs.push([s0, last]);
        const mass = (sg) => { let n = 0; for (let i = sg[0]; i <= sg[1]; i++) n += colInk[i]; return n; };
        // isolated slivers (board-edge scratches, stray marks) far from their neighbours are dropped
        const good = segs.filter((sg, i) => {
          if (mass(sg) >= 0.12 * lh * lh) return true;
          const gl = i > 0 ? sg[0] - segs[i - 1][1] : Infinity, gr = i < segs.length - 1 ? segs[i + 1][0] - sg[1] : Infinity;
          return Math.min(gl, gr) < 0.5 * lh;
        });
        const groups = [];
        good.forEach((sg) => {
          const g = groups[groups.length - 1];
          if (g && sg[0] - g[1] <= 2.5 * lh) g[1] = sg[1]; else groups.push([sg[0], sg[1]]);
        });
        groups.forEach(([ga, gb]) => {
          if (gb - ga < 0.6 * lh) return;
          const pad = Math.round(0.25 * lh), keep = Math.round(0.15 * lh);
          const px0 = Math.max(0, x0 + ga - pad), px1 = Math.min(W, x0 + gb + pad);
          const py0 = Math.max(0, ya - pad), py1 = Math.min(H, yb + pad);
          // rows outside this line's band (+ a small margin) are blanked, so parts of the lines above and below don't leak in
          pieces.push({ x: px0, y: py0, w: px1 - px0, h: py1 - py0, keepTop: Math.max(0, ya - keep - py0), keepBottom: Math.min(py1, yb + keep) - py0 });
        });
      });
    });
    return pieces;
  }

  function tidyHand(t) {
    t = t.replace(/[_]{2,}.*/g, '').replace(/\s+/g, ' ').trim();
    const toks = t.split(' ');
    if (toks.length >= 3 && toks.filter((w) => w.replace(/[^A-Za-z]/g, '').length <= 1).length / toks.length > 0.6) return '';
    if (t.replace(/[^A-Za-z0-9]/g, '').length < 2) return '';
    return t;
  }

  async function readHandwriting(cleaned) {
    const reader = await getHandReader();
    const pieces = segmentLines(cleaned);
    const out = [];
    for (let i = 0; i < pieces.length; i++) {
      setProgress(0.5 + 0.5 * (i / pieces.length), null);
      $('#ocr-status').textContent = `${t('stHandLine')} ${i + 1} ${t('stOf')} ${pieces.length}…`;
      const pc = pieces[i], crop = document.createElement('canvas');
      crop.width = pc.w; crop.height = pc.h;
      const cg = crop.getContext('2d');
      cg.drawImage(cleaned, pc.x, pc.y, pc.w, pc.h, 0, 0, pc.w, pc.h);
      cg.fillStyle = '#fff';
      cg.fillRect(0, 0, pc.w, pc.keepTop);
      cg.fillRect(0, pc.keepBottom, pc.w, pc.h - pc.keepBottom);
      const res = await reader(crop.toDataURL('image/png'));
      const line = tidyHand((res[0] && res[0].generated_text) || '');
      if (line) out.push(line);
    }
    return out.join('\n');
  }

  function updateEngineUi() {
    $$('#seg-engine button').forEach((b) => b.classList.toggle('on', b.dataset.v === settings.engine));
    $('#hand-note').hidden = settings.engine !== 'hand';
  }
  $$('#seg-engine button').forEach((b) => b.addEventListener('click', () => { settings.engine = b.dataset.v; store('kl.settings', settings); updateEngineUi(); }));

  $('#btn-convert').addEventListener('click', async () => {
    if (!state.source) return;
    const btn = $('#btn-convert');
    btn.disabled = true;
    setProgress(0.02, 'stLoading');
    try {
      let text;
      if (settings.engine === 'hand') {
        if (OPENED_AS_FILE) throw new Error('file mode');
        const cleaned = cleanImage(state.source, Object.assign(currentOpts(), { bw: false }));
        try { text = await readHandwriting(cleaned); }
        catch (e) { console.error(e); state.hand = null; toast(t('handFail'), 8000); return; }
        state.unsure = new Set();
      } else {
        const worker = await getWorker();
        const cleaned = cleanImage(state.source, currentOpts());
        const { data } = await worker.recognize(cleaned, {}, { text: true, blocks: true });
        const lines = linesFromOcr(data);
        text = joinLines(lines.map((l) => l.map((w) => w.text)));
        state.unsure = new Set(lines.flat().filter((w) => w.conf < 70).map((w) => w.text.replace(/[^A-Za-z0-9'’]/g, '')));
      }
      setProgress(1, 'stDone');
      if (!text) { toast(t('noText')); return; }
      openText(text, null, null, state.unsure);
    } catch (err) {
      console.error(err);
      // start a fresh reading engine next time instead of reusing a broken one
      if (state.worker) { try { state.worker.terminate(); } catch (e) { /* already gone */ } state.worker = null; }
      if (OPENED_AS_FILE) toast(t('fileMode'), 9000);
      else toast(t('ocrFail') + ' (' + String((err && err.message) || err).slice(0, 90) + ')', 7000);
    } finally {
      btn.disabled = false;
      setTimeout(() => { $('#ocr-progress').hidden = true; }, 600);
    }
  });

  /* ---------------- READ: dyslexia-friendly view ---------------- */
  function openText(text, noteId, lang, unsure) {
    state.text = text;
    state.unsure = unsure || new Set();
    state.noteId = noteId;
    state.textLang = lang || detectLang(text);
    updateTextLangChip();
    renderReader();
    updateVoiceNote();
    show('reader');
  }

  function applyDisplay() {
    const root = document.documentElement.style;
    const [bg, ink] = BG[settings.bg] || BG.cream;
    root.setProperty('--r-bg', bg);
    root.setProperty('--r-ink', ink);
    root.setProperty('--r-size', settings.size + 'px');
    root.setProperty('--r-lh', settings.spacing);
    root.setProperty('--r-font', settings.font === 'dyslexic' ? '"OpenDyslexic", Verdana, sans-serif' : 'Verdana, "DejaVu Sans", sans-serif');
    $('#reader').classList.toggle('dark', settings.bg === 'dark');
    $('#reader').classList.toggle('focus', settings.focus);
    $$('#seg-font button').forEach((b) => b.classList.toggle('on', b.dataset.v === settings.font));
    $$('#swatches button').forEach((b) => b.classList.toggle('on', b.dataset.v === settings.bg));
    $('#opt-size').value = settings.size;
    $('#opt-spacing').value = settings.spacing;
    $('#opt-rate').value = settings.rate;
    $('#opt-focus').checked = settings.focus;
    $('#btn-syll').setAttribute('aria-pressed', String(settings.syll));
  }
  function saveDisplay() { store('kl.settings', settings); applyDisplay(); }

  $$('#seg-font button').forEach((b) => b.addEventListener('click', () => { settings.font = b.dataset.v; saveDisplay(); }));
  $$('#swatches button').forEach((b) => b.addEventListener('click', () => { settings.bg = b.dataset.v; saveDisplay(); }));
  $('#opt-size').addEventListener('input', (e) => { settings.size = +e.target.value; saveDisplay(); });
  $('#opt-spacing').addEventListener('input', (e) => { settings.spacing = +e.target.value; saveDisplay(); });
  $('#opt-rate').addEventListener('input', (e) => { settings.rate = +e.target.value; saveDisplay(); });
  $('#opt-focus').addEventListener('change', (e) => { settings.focus = e.target.checked; saveDisplay(); });
  $('#btn-syll').addEventListener('click', () => { settings.syll = !settings.syll; saveDisplay(); renderReader(); });
  $('#btn-display').addEventListener('click', () => {
    const panel = $('#display-panel');
    panel.hidden = !panel.hidden;
    $('#btn-display').setAttribute('aria-expanded', String(!panel.hidden));
  });

  function splitSentences(paragraph) {
    const out = paragraph.match(/[^.!?]+[.!?]+["')\]]*\s*|[^.!?]+$/g);
    return (out || [paragraph]).map((s) => s.trim()).filter(Boolean);
  }

  function renderReader() {
    const reader = $('#reader');
    reader.innerHTML = '';
    state.sentences = [];
    const paragraphs = state.text.split(/\n+/).map((p) => p.trim()).filter(Boolean);
    paragraphs.forEach((para) => {
      const p = document.createElement('p');
      splitSentences(para).forEach((sentence, si) => {
        if (si) p.appendChild(document.createTextNode(' '));
        const sEl = document.createElement('span');
        sEl.className = 's';
        const record = { el: sEl, text: sentence, words: [] };
        const re = /[A-Za-z0-9'’]+|[^A-Za-z0-9'’]+/g;
        let m;
        while ((m = re.exec(sentence))) {
          const tok = m[0];
          if (/^[A-Za-z0-9'’]+$/.test(tok)) {
            const w = document.createElement('span');
            w.className = 'w';
            w.dataset.word = tok;
            if (state.unsure.has(tok)) { w.classList.add('unsure'); w.title = t('unsure'); }
            if (settings.syll) {
              Syllables.split(tok, state.textLang).forEach((part, i) => {
                if (i) {
                  const dot = document.createElement('span');
                  dot.className = 'syl-dot'; dot.textContent = '·'; dot.setAttribute('aria-hidden', 'true');
                  w.appendChild(dot);
                }
                w.appendChild(document.createTextNode(part));
              });
            } else {
              w.textContent = tok;
            }
            sEl.appendChild(w);
            record.words.push({ el: w, start: m.index, end: m.index + tok.length, text: tok });
          } else {
            sEl.appendChild(document.createTextNode(tok));
          }
        }
        p.appendChild(sEl);
        state.sentences.push(record);
      });
      reader.appendChild(p);
    });
    reader.classList.add('idle');
    $('#unsure-note').hidden = !$('#reader .unsure');
  }

  $('#reader').addEventListener('click', (e) => {
    const w = e.target.closest('.w');
    if (!w) return;
    stopSpeech();
    const word = w.dataset.word;
    w.classList.add('current');
    const text = settings.syll ? Syllables.split(word, state.textLang).join(' - ') + '. ' + word : word;
    speak(text, Math.max(0.5, settings.rate - 0.1), null, () => w.classList.remove('current'));
  });

  /* ---------------- READ: text-to-speech ---------------- */
  const synth = window.speechSynthesis;
  const VOICE_PREF = { en: ['en-ZA', 'en-GB', 'en-US', 'en'], sn: ['sn', 'sw', 'zu', 'xh', 'ny', 'en-ZA', 'en'] };

  function voices() { return synth ? synth.getVoices() : []; }
  function pickVoice(lang) {
    const list = voices();
    for (const pref of VOICE_PREF[lang]) {
      const v = list.find((x) => x.lang && x.lang.replace('_', '-').toLowerCase().startsWith(pref.toLowerCase()));
      if (v) return v;
    }
    return list[0] || null;
  }
  function updateVoiceNote() {
    const note = $('#voice-note');
    if (!synth) { note.textContent = t('noVoice'); return; }
    const v = pickVoice(state.textLang);
    if (!v) { note.textContent = ''; return; }
    let msg = t('voiceUsing') + v.name + ' (' + v.lang + ')';
    if (state.textLang === 'sn' && !/^sn/i.test(v.lang)) msg += '. ' + t('voiceFallbackSn');
    note.textContent = msg;
  }
  if (synth) synth.addEventListener && synth.addEventListener('voiceschanged', updateVoiceNote);

  function speak(text, rate, onBoundary, onEnd) {
    if (!synth) { toast(t('noVoice')); return null; }
    const u = new SpeechSynthesisUtterance(text);
    const v = pickVoice(state.textLang);
    if (v) { u.voice = v; u.lang = v.lang; } else { u.lang = state.textLang === 'sn' ? 'sn' : 'en'; }
    u.rate = rate;
    if (onBoundary) u.onboundary = onBoundary;
    u.onend = onEnd;
    u.onerror = onEnd;
    synth.speak(u);
    return u;
  }

  function clearHighlights() {
    $$('#reader .current').forEach((el) => el.classList.remove('current'));
  }

  function playFrom(idx) {
    clearHighlights();
    if (idx >= state.sentences.length) { stopSpeech(); return; }
    state.sentIdx = idx;
    const s = state.sentences[idx];
    s.el.classList.add('current');
    $('#reader').classList.remove('idle');
    s.el.scrollIntoView({ block: 'center', behavior: 'smooth' });
    let token = state.token = {};
    speak(s.text, settings.rate, (ev) => {
      if (ev.name && ev.name !== 'word') return;
      const w = s.words.find((x) => ev.charIndex >= x.start && ev.charIndex < x.end) ||
                s.words.find((x) => x.start >= ev.charIndex);
      s.words.forEach((x) => x.el.classList.remove('current'));
      if (w) w.el.classList.add('current');
    }, () => {
      if (state.playing && state.token === token) playFrom(idx + 1);
    });
  }

  function updatePlayButton() {
    const b = $('#btn-play');
    b.classList.toggle('playing', state.playing);
    b.querySelector('[data-i18n]').textContent = state.playing ? t('pause') : t('listen');
  }

  function stopSpeech() {
    state.playing = false;
    state.token = null;
    if (synth) synth.cancel();
    clearHighlights();
    const r = $('#reader'); if (r) r.classList.add('idle');
    updatePlayButton();
  }

  $('#btn-play').addEventListener('click', () => {
    if (!state.sentences.length) return;
    if (state.playing) {               // pause: remember the sentence and stop (pause() is unreliable on Android)
      const keep = state.sentIdx;
      stopSpeech();
      state.sentIdx = keep;
      return;
    }
    state.playing = true;
    updatePlayButton();
    if (synth) synth.cancel();
    playFrom(state.sentIdx >= state.sentences.length ? 0 : state.sentIdx);
  });
  $('#btn-stop').addEventListener('click', () => { stopSpeech(); state.sentIdx = 0; });

  /* ---------------- Fix / type text ---------------- */
  let editReturn = 'reader';
  $('#btn-edit').addEventListener('click', () => {
    $('#edit-text').value = state.text; editReturn = 'reader'; show('edit');
  });
  $('#btn-type').addEventListener('click', () => {
    $('#edit-text').value = ''; state.noteId = null; editReturn = 'home'; show('edit');
    $('#edit-text').focus();
  });
  $('#btn-edit-cancel').addEventListener('click', () => show(editReturn));
  $('#btn-edit-done').addEventListener('click', () => {
    const text = $('#edit-text').value.trim();
    if (!text) { show(editReturn); return; }
    const keepLang = editReturn === 'reader' ? state.textLang : null;
    state.sentIdx = 0;
    openText(text, state.noteId, keepLang);
  });

  /* ---------------- Notes ---------------- */
  const getNotes = () => load('kl.notes', []);
  const putNotes = (n) => store('kl.notes', n);

  $('#btn-save').addEventListener('click', () => {
    const notes = getNotes();
    const firstLine = state.text.split('\n')[0].slice(0, 48);
    if (state.noteId) {
      const n = notes.find((x) => x.id === state.noteId);
      if (n) { n.text = state.text; n.lang = state.textLang; n.title = firstLine; n.updated = Date.now(); }
    } else {
      state.noteId = 'n' + Date.now();
      notes.unshift({ id: state.noteId, title: firstLine || t('untitled'), text: state.text, lang: state.textLang, created: Date.now() });
    }
    putNotes(notes);
    toast(t('saved'));
  });

  function noteItem(n, withDelete) {
    const li = document.createElement('li');
    const open = document.createElement('button');
    open.type = 'button'; open.className = 'note-open';
    const b = document.createElement('b'); b.textContent = n.title || t('untitled');
    const s = document.createElement('small');
    s.textContent = new Date(n.created).toLocaleDateString(settings.ui === 'sn' ? 'en-ZW' : undefined,
      { day: 'numeric', month: 'short', year: 'numeric' }) + ' · ' + t('langName')[n.lang || 'en'];
    open.append(b, s);
    open.addEventListener('click', () => { state.sentIdx = 0; openText(n.text, n.id, n.lang); });
    li.appendChild(open);
    if (withDelete) {
      const del = document.createElement('button');
      del.type = 'button'; del.className = 'note-del'; del.setAttribute('aria-label', 'Delete');
      del.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 19a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>';
      del.addEventListener('click', () => {
        if (!confirm(t('deleteQ'))) return;
        putNotes(getNotes().filter((x) => x.id !== n.id));
        renderNotes(); toast(t('deleted'));
      });
      li.appendChild(del);
    }
    return li;
  }
  function renderNotes() {
    const list = $('#notes-list'); list.innerHTML = '';
    const notes = getNotes();
    notes.forEach((n) => list.appendChild(noteItem(n, true)));
    $('#notes-empty').hidden = notes.length > 0;
  }
  function renderRecent() {
    const list = $('#recent-list'); list.innerHTML = '';
    const notes = getNotes().slice(0, 3);
    notes.forEach((n) => list.appendChild(noteItem(n, false)));
    $('#recent-card').hidden = notes.length === 0;
  }

  /* ---------------- Install (no Play Store needed) ---------------- */
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    state.installEvt = e;
    $('#btn-install').hidden = false;
  });
  $('#btn-install').addEventListener('click', async () => {
    if (state.installEvt) {
      state.installEvt.prompt();
      await state.installEvt.userChoice;
      state.installEvt = null;
      $('#btn-install').hidden = true;
    } else {
      toast(t('iosInstall'));
    }
  });
  const isIos = /iphone|ipad|ipod/i.test(navigator.userAgent);
  const standalone = window.matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  if (isIos && !standalone) $('#btn-install').hidden = false;

  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
  }

  /* ---------------- Start ---------------- */
  // Browsers block the OCR engine (web worker + WebAssembly) for pages opened as files; warn up front
  const OPENED_AS_FILE = location.protocol === 'file:';
  if (OPENED_AS_FILE) $('#file-warning').hidden = false;
  state.textLang = settings.ui;
  applyUiLang();
  applyDisplay();
  renderRecent();

  // used by the demo/screenshot script
  updateEngineUi();
  window.KL = { openText, show, loadFile, cleanImage, linesFromOcr, joinLines, getWorker, meanLuma, state, segmentLines };
})();
