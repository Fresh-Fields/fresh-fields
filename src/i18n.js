import i18next from 'i18next';

i18next.init({
  lng: 'en',
  debug: true,
  resources: {
    en: {
      translation: {
        "test": "enter data"
      }
    },
    hi: {
      translation: {
        "test": "डेटा दर्ज करें"
      }
    }
  }
});

document.getElementById('test-i18n').innerHTML = i18next.t('test', { lng: 'hi' });

// i18next(document.querySelector('container'));