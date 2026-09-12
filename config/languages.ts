export type LanguageConfig = {
  code: string;
  displayName: string;
  nativeName: string;
  script: string;
  asr: boolean;
  translation: boolean;
  tts: boolean;
  direction: 'ltr' | 'rtl';
  indicTrans2Code: string | null;
  indicConformerCode: string | null;
};

export const LANGUAGES: LanguageConfig[] = [
  ['as','Assamese','অসমীয়া','Bengali',true,true,true,'ltr','as','as'],
  ['bn','Bengali','বাংলা','Bengali',true,true,true,'ltr','bn','bn'],
  ['brx','Bodo','बड़ो','Devanagari',true,true,true,'ltr','brx','brx'],
  ['doi','Dogri','डोगरी','Devanagari',true,true,true,'ltr','doi','doi'],
  ['en','English','English','Latin',false,true,true,'ltr',null,null],
  ['gu','Gujarati','ગુજરાતી','Gujarati',true,true,true,'ltr','gu','gu'],
  ['hi','Hindi','हिन्दी','Devanagari',true,true,true,'ltr','hi','hi'],
  ['kn','Kannada','ಕನ್ನಡ','Kannada',true,true,true,'ltr','kn','kn'],
  ['gom','Konkani','कोंकणी','Devanagari',true,true,true,'ltr','gom','gom'],
  ['ks','Kashmiri','कॉशुर / کٲشُر','Arabic/Devanagari',true,true,true,'ltr','ks','ks'],
  ['mai','Maithili','मैथिली','Devanagari',true,true,true,'ltr','mai','mai'],
  ['ml','Malayalam','മലയാളം','Malayalam',true,true,true,'ltr','ml','ml'],
  ['mni','Manipuri','মৈতৈলোন্','Bengali',true,true,true,'ltr','mni','mni'],
  ['mr','Marathi','मराठी','Devanagari',true,true,true,'ltr','mr','mr'],
  ['ne','Nepali','नेपाली','Devanagari',true,true,true,'ltr','ne','ne'],
  ['or','Odia','ଓଡ଼ିଆ','Odia',true,true,true,'ltr','or','or'],
  ['pa','Punjabi','ਪੰਜਾਬੀ','Gurmukhi',true,true,true,'ltr','pa','pa'],
  ['sa','Sanskrit','संस्कृतम्','Devanagari',true,true,true,'ltr','sa','sa'],
  ['sat','Santali','ᱥᱟᱱᱛᱟᱲᱤ','Ol Chiki',true,true,true,'ltr','sat','sat'],
  ['sd','Sindhi','سنڌي','Arabic',true,true,true,'rtl','snd','snd'],
  ['ta','Tamil','தமிழ்','Tamil',true,true,true,'ltr','ta','ta'],
  ['te','Telugu','తెలుగు','Telugu',true,true,true,'ltr','te','te'],
  ['ur','Urdu','اردو','Arabic',true,true,true,'rtl','ur','ur'],
].map(([code,displayName,nativeName,script,asr,translation,tts,direction,indicTrans2Code,indicConformerCode]) => ({
  code, displayName, nativeName, script, asr, translation, tts, direction, indicTrans2Code, indicConformerCode
}));

export const LANGUAGE_MAP = Object.fromEntries(LANGUAGES.map((l) => [l.code, l]));
