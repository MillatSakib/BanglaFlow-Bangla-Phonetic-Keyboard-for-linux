import rawRules from './phonetic_rules.js';

// Initialize sets and preprocess patterns
const vowels = new Set(rawRules.vowel.split(''));
const consonants = new Set(rawRules.consonant.split(''));
const casesensitive = new Set(rawRules.casesensitive.split(''));

// Parse and normalize rule patterns
const patterns = rawRules.patterns.map(p => {
  const rules = (p.rules || []).map(r => {
    const matches = (r.matches || []).map(m => {
      const scopeStr = m.scope || '';
      const isNeg = m.negative || scopeStr.startsWith('!');
      const cleanScope = scopeStr.replace(/^!+/, '');
      return {
        type: m.type,
        scope: cleanScope,
        value: m.value || '',
        negative: isNeg
      };
    });
    return { replace: r.replace, matches };
  });
  return { find: p.find, replace: p.replace, rules };
});

// Deterministic longest-match sort: longest find first; if same length, alphabetical
patterns.sort((a, b) => {
  if (b.find.length !== a.find.length) {
    return b.find.length - a.find.length;
  }
  return a.find.localeCompare(b.find);
});

// Normalize case according to case-sensitivity table
function fixString(text) {
  let res = '';
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (casesensitive.has(c.toLowerCase())) {
      res += c;
    } else {
      res += c.toLowerCase();
    }
  }
  return res;
}

// Convert a single token/word using Avro phonetic rules
export function convertAvroWord(text, bengaliDigits = true, mapDari = true) {
  if (!text) return '';
  const fixedStr = fixString(text);
  const length = fixedStr.length;
  const output = [];
  let cur = 0;

  while (cur < length) {
    const start = cur;
    let matched = false;

    // Digits
    const ch = fixedStr[cur];
    if (ch >= '0' && ch <= '9') {
      if (bengaliDigits) {
        const bnDigit = String.fromCharCode(0x09e6 + (ch.charCodeAt(0) - 48));
        output.push(bnDigit);
      } else {
        output.push(ch);
      }
      cur++;
      continue;
    }

    // Dari and Punctuation
    if (mapDari && ch === '.') {
      if (cur + 1 < length && fixedStr[cur + 1] === '.') {
        output.push('\u0965'); // ॥
        cur += 2;
        continue;
      } else if (cur + 1 < length && fixedStr[cur + 1] === '`') {
        output.push('.');
        cur += 2;
        continue;
      } else {
        output.push('\u0964'); // ।
        cur += 1;
        continue;
      }
    }

    // Currency
    if (ch === '$') {
      output.push('৳');
      cur++;
      continue;
    }

    // Match patterns
    for (let pIdx = 0; pIdx < patterns.length; pIdx++) {
      const pattern = patterns[pIdx];
      const findLen = pattern.find.length;
      const end = cur + findLen;

      if (end <= length && fixedStr.slice(start, end) === pattern.find) {
        const prev = start - 1;

        if (pattern.rules && pattern.rules.length > 0) {
          for (let rIdx = 0; rIdx < pattern.rules.length; rIdx++) {
            const rule = pattern.rules[rIdx];
            let replaceOk = true;

            for (let mIdx = 0; mIdx < rule.matches.length; mIdx++) {
              const m = rule.matches[mIdx];
              const chk = m.type === 'suffix' ? end : prev;
              const scope = m.scope;
              let cond = false;

              if (scope === 'punctuation') {
                const outOfBounds = m.type === 'prefix' ? chk < 0 : chk >= length;
                cond = outOfBounds || (!vowels.has(fixedStr[chk].toLowerCase()) && !consonants.has(fixedStr[chk].toLowerCase()));
              } else if (scope === 'vowel') {
                const inBounds = m.type === 'prefix' ? chk >= 0 : chk < length;
                cond = inBounds && vowels.has(fixedStr[chk].toLowerCase());
              } else if (scope === 'consonant') {
                const inBounds = m.type === 'prefix' ? chk >= 0 : chk < length;
                cond = inBounds && consonants.has(fixedStr[chk].toLowerCase());
              } else if (scope === 'exact') {
                const val = m.value;
                let s, e;
                if (m.type === 'suffix') {
                  s = end;
                  e = end + val.length;
                } else {
                  s = start - val.length;
                  e = start;
                }
                cond = s >= 0 && e <= length && fixedStr.slice(s, e) === val;
              }

              if (m.negative) {
                cond = !cond;
              }

              if (!cond) {
                replaceOk = false;
                break;
              }
            }

            if (replaceOk) {
              output.push(rule.replace);
              cur = end;
              matched = true;
              break;
            }
          }
        }

        if (matched) break;

        output.push(pattern.replace);
        cur = end;
        matched = true;
        break;
      }
    }

    if (!matched) {
      output.push(fixedStr[cur]);
      cur++;
    }
  }

  return output.join('');
}

// Common dictionary mappings for natural Banglish words and popular phrases
// to ensure perfect transliteration even if users don't use strict Avro uppercase rules
export const COMMON_DICTIONARY = {
  // Frequently typed natural words
  'sonar': 'সোনার',
  'sOnar': 'সোনার',
  'amar': 'আমার',
  'bangla': 'বাংলা',
  'ami': 'আমি',
  'amra': 'আমরা',
  'amader': 'আমাদের',
  'tumi': 'তুমি',
  'tomar': 'তোমার',
  'tomay': 'তোমায়',
  'tomake': 'তোমাকে',
  'tomra': 'তোমরা',
  'tomader': 'তোমাদের',
  'apni': 'আপনি',
  'apnar': 'আপনার',
  'apnader': 'আপনাদের',
  'she': 'সে',
  'tini': 'তিনি',
  'tader': 'তাদের',
  'valobashi': 'ভালোবাসি',
  'valobasi': 'ভালোবাসি',
  'bhalobashi': 'ভালোবাসি',
  'bhalobasi': 'ভালোবাসি',
  'valo': 'ভালো',
  'bhalo': 'ভালো',
  'banglaflow': 'বাংলাফ্লো',
  'somossa': 'সমস্যা',
  'somossya': 'সমস্যা',
  'dhonnobad': 'ধন্যবাদ',
  'shagotom': 'স্বাগতম',
  'du:kho': 'দুঃখ',
  'dukho': 'দুঃখ',
  'shadhinota': 'স্বাধীনতা',
  'kichu': 'কিছু',
  'shob': 'সব',
  'shobai': 'সবাই',
  'shobaike': 'সবাইকে',
  'shobaik': 'সবাইকে',
  'shobar': 'সবার',
  'desh': 'দেশ',
  'onek': 'অনেক',
  'kemon': 'কেমন',
  'acho': 'আছো',
  'achho': 'আছো',
  'achhi': 'আছি',
  'achi': 'আছি',
  'ache': 'আছে',
  'bhasha': 'ভাষা',
  'sahajjo': 'সাহায্য',
  'sohoj': 'সহজ',
  'shobdo': 'শব্দ',
  'manush': 'মানুষ',
  'bondhu': 'বন্ধু',
  'protidin': 'প্রতিদিন',
  'shokal': 'সকাল',
  'shondha': 'সন্ধ্যা',
  'raat': 'রাত',
  'shanti': 'শান্তি',
  'mon': 'মন',
  'khushi': 'খুশি',
  'prothom': 'প্রথম',
  'shesh': 'শেষ',
  'ekhon': 'এখন',
  'shathe': 'সাথে',
  'sathe': 'সাথে',
  'kotha': 'কথা',
  'gaan': 'গান',
  'kobita': 'কবিতা',
  'shundor': 'সুন্দর',
  'sundor': 'সুন্দর',
  'c^ad': 'চাঁদ',
  'ca^d': 'চাঁদ'
};

/**
 * Full contextual transliteration engine.
 * Splits text into words and delimiters, applying dictionary intelligence
 * while falling back to the full longest-match Avro phonetic engine.
 */
export function transliterate(text, options = {}) {
  if (!text) return '';
  const { bengaliDigits = true, mapDari = true } = options;

  // Split text by whitespace, preserving whitespace separators
  const tokens = text.split(/(\s+)/);

  return tokens.map(token => {
    if (!token) return '';
    // If token is purely whitespace, preserve it
    if (/^\s+$/.test(token)) {
      return token;
    }

    // Match leading punctuation, core phonetic text, and trailing punctuation
    // Note: : ` ^ $ are treated as phonetic modifiers rather than boundary punctuation
    const match = token.match(/^([^a-zA-Z0-9:`^$]*)([a-zA-Z0-9:`^$]+)(.*)$/);
    if (!match) {
      return convertAvroWord(token, bengaliDigits, mapDari);
    }

    const [, leadingPunct, coreText, trailingPunct] = match;
    const lower = coreText.toLowerCase();

    let convertedCore;
    if (COMMON_DICTIONARY[lower]) {
      convertedCore = COMMON_DICTIONARY[lower];
    } else {
      convertedCore = convertAvroWord(coreText, bengaliDigits, mapDari);
    }

    // If trailing punctuation contains a period, convert it to Dari if mapDari is true
    let convertedTrailing = trailingPunct;
    if (mapDari && convertedTrailing) {
      convertedTrailing = convertedTrailing.replace(/\.\./g, '॥').replace(/\./g, '।');
    }

    return leadingPunct + convertedCore + convertedTrailing;
  }).join('');
}
