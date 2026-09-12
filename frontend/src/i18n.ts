import { LANGUAGES } from '../../config/languages';

export const supportedLanguages = LANGUAGES.map((language) => language.code);
export const uiStrings = {
  en: { title: 'Rural Healthcare Orchestrator', triage: 'Run AI Triage' },
  hi: { title: 'ग्रामीण स्वास्थ्य सेवा', triage: 'एआई ट्रायेज चलाएं' },
  mr: { title: 'ग्रामीण आरोग्य सेवा', triage: 'एआय ट्रायेज चालवा' },
  ta: { title: 'கிராமப்புற சுகாதார சேவை', triage: 'AI பரிசோதனையை இயக்கவும்' },
  te: { title: 'గ్రామీణ ఆరోగ్య సేవ', triage: 'AI ట్రయాజ్ ప్రారంభించండి' },
};
