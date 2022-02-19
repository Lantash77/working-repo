# -*- coding: utf-8 -*-

"""
    VIKI Rakuten® addon Add-on

"""
import xbmcaddon


my_addon = xbmcaddon.Addon()
my_addon_id = my_addon.getAddonInfo('id')
getSetting = my_addon.getSetting
L = my_addon.getLocalizedString

languagelist = [{'lang': 'en', 'code': '0', 'language': 'English'},
				{'lang': 'bg', 'code': '1', 'language': 'Bulgarian'},
				{'lang': 'es', 'code': '2', 'language': 'Spanish'},
				{'lang': 'fr', 'code': '3', 'language': 'French'},
				{'lang': 'pt', 'code': '4', 'language': 'Portuguese'},
				{'lang': 'ja', 'code': '5', 'language': 'Japanese'},
				{'lang': 'zh', 'code': '6', 'language': 'Chinese'},
				{'lang': 'tw', 'code': '7', 'language': 'Taiwanese'},
				{'lang': 'ko', 'code': '8', 'language': 'Korean'},
				{'lang': 'ab', 'code': '9', 'language': 'Abkhazian'},
				{'lang': 'aa', 'code': '10', 'language': 'Afar'},
				{'lang': 'af', 'code': '11', 'language': 'Afrikaans'},
				{'lang': 'ak', 'code': '12', 'language': 'Akana'},
				{'lang': 'am', 'code': '13', 'language': 'Amharic'},
				{'lang': 'ag', 'code': '14', 'language': 'English'},
				{'lang': 'az', 'code': '15', 'language': 'Azerbaijani'},
				{'lang': 'ms', 'code': '16', 'language': 'Malay'},
				{'lang': 'id', 'code': '17', 'language': 'Indonesian'},
				{'lang': 'jv', 'code': '18', 'language': 'Basa Jawa'},
				{'lang': 'bn', 'code': '19', 'language': 'Bengali'},
				{'lang': 'bo', 'code': '20', 'language': 'Tibetan'},
				{'lang': 'bs', 'code': '21', 'language': 'Bosanski'},
				{'lang': 'ca', 'code': '22', 'language': 'Catalan'},
				{'lang': 'ch', 'code': '23', 'language': 'Chamoru'},
				{'lang': 'ce', 'code': '24', 'language': 'Cherokee'},
				{'lang': 'za', 'code': '25', 'language': 'Cuengh'},
				{'lang': 'cy', 'code': '26', 'language': 'Welsh'},
				{'lang': 'da', 'code': '27', 'language': 'Danish'},
				{'lang': 'de', 'code': '28', 'language': 'German'},
				{'lang': 'dv', 'code': '29', 'language': 'Divehi'},
				{'lang': 'dz', 'code': '30', 'language': 'Bhutani'},
				{'lang': 'et', 'code': '31', 'language': 'Estonian'},
				{'lang': 'eo', 'code': '32', 'language': 'Esperanto'},
				{'lang': 'eu', 'code': '33', 'language': 'Basque'},
				{'lang': 'to', 'code': '34', 'language': 'Tonga'},
				{'lang': 'ga', 'code': '35', 'language': 'Irish'},
				{'lang': 'sm', 'code': '36', 'language': 'Samoan'},
				{'lang': 'gl', 'code': '37', 'language': 'Galician'},
				{'lang': 'gd', 'code': '38', 'language': 'Scots Gaelic'},
				{'lang': 'hm', 'code': '39', 'language': 'Hmong'},
				{'lang': 'hr', 'code': '40', 'language': 'Croatian'},
				{'lang': 'ia', 'code': '41', 'language': 'Interlingua'},
				{'lang': 'it', 'code': '42', 'language': 'Italian'},
				{'lang': 'mu', 'code': '43', 'language': 'Karaoke'},
				{'lang': 'cb', 'code': '44', 'language': 'Kaszëbsczi'},
				{'lang': 'kw', 'code': '45', 'language': 'Kernewek/Karnuack'},
				{'lang': 'km', 'code': '46', 'language': 'Cambodian'},
				{'lang': 'rn', 'code': '47', 'language': 'Kirundi'},
				{'lang': 'sw', 'code': '48', 'language': 'Swahili'},
				{'lang': 'hat', 'code': '49', 'language': 'Kreyòlayisyen'},
				{'lang': 'ku', 'code': '50', 'language': 'Kurdish'},
				{'lang': 'lo', 'code': '51', 'language': 'Laothian'},
				{'lang': 'la', 'code': '52', 'language': 'Latin'},
				{'lang': 'lv', 'code': '53', 'language': 'Latvian'},
				{'lang': 'lt', 'code': '54', 'language': 'Lithuanian'},
				{'lang': 'hu', 'code': '55', 'language': 'Hungarian'},
				{'lang': 'mg', 'code': '56', 'language': 'Malagasy'},
				{'lang': 'ml', 'code': '57', 'language': 'Malayalam'},
				{'lang': 'mo', 'code': '58', 'language': 'Moldavian'},
				{'lang': 'my', 'code': '59', 'language': 'Burmese'},
				{'lang': 'fj', 'code': '60', 'language': 'Fiji'},
				{'lang': 'nl', 'code': '61', 'language': 'Dutch'},
				{'lang': 'cr', 'code': '62', 'language': 'Nehiyaw'},
				{'lang': 'no', 'code': '63', 'language': 'Norwegian'},
				{'lang': 'or', 'code': '64', 'language': 'Oriya'},
				{'lang': 'uz', 'code': '65', 'language': 'Uzbek'},
				{'lang': 'pl', 'code': '66', 'language': 'Polski'},
				{'lang': 'ro', 'code': '67', 'language': 'Romanian'},
				{'lang': 'rm', 'code': '68', 'language': 'Rhaeto-Romance'},
				{'lang': 'st', 'code': '69', 'language': 'Sesotho'},
				{'lang': 'sq', 'code': '70', 'language': 'Albanian'},
				{'lang': 'sk', 'code': '71', 'language': 'Slovak'},
				{'lang': 'sl', 'code': '72', 'language': 'Slovenian'},
				{'lang': 'so', 'code': '73', 'language': 'Somali'},
				{'lang': 'sh', 'code': '74', 'language': 'Serbo-Croatian'},
				{'lang': 'fi', 'code': '75', 'language': 'Finnish'},
				{'lang': 'sv', 'code': '76', 'language': 'Swedish'},
				{'lang': 'tl', 'code': '77', 'language': 'Tagalog'},
				{'lang': 'tt', 'code': '78', 'language': 'Tatar'},
				{'lang': 'vi', 'code': '79', 'language': 'Vietnamese'},
				{'lang': 'tw', 'code': '80', 'language': 'Twi'},
				{'lang': 'tr', 'code': '81', 'language': 'Turkish'},
				{'lang': 'wo', 'code': '82', 'language': 'Wolof'},
				{'lang': 'yo', 'code': '83', 'language': 'Yoruba'},
				{'lang': 'sn', 'code': '84', 'language': 'Shona'},
				{'lang': 'lol', 'code': '85', 'language': 'lolspeak'},
				{'lang': 'tm', 'code': '86', 'language': 'tlh Ingan-Hol'},
				{'lang': 'is', 'code': '87', 'language': 'Icelandic'},
				{'lang': 'cs', 'code': '88', 'language': 'Czech'},
				{'lang': 'el', 'code': '89', 'language': 'Greek'},
				{'lang': 'ba', 'code': '90', 'language': 'Bashkir'},
				{'lang': 'mk', 'code': '91', 'language': 'Macedonian'},
				{'lang': 'mn', 'code': '92', 'language': 'Mongolian'},
				{'lang': 'ru', 'code': '93', 'language': 'Russian'},
				{'lang': 'sr', 'code': '94', 'language': 'Serbian'},
				{'lang': 'uk', 'code': '95', 'language': 'Ukrainian'},
				{'lang': 'mne', 'code': '96', 'language': 'црногорски'},
				{'lang': 'kk', 'code': '97', 'language': 'Kazakh'},
				{'lang': 'hy', 'code': '98', 'language': 'Armenian'},
				{'lang': 'he', 'code': '99', 'language': 'Hebrew'},
				{'lang': 'ar', 'code': '100', 'language': 'Arabic'},
				{'lang': 'ur', 'code': '101', 'language': 'Urdu'},
				{'lang': 'skr', 'code': '102', 'language': 'سرائیکی'},
				{'lang': 'fa', 'code': '103', 'language': 'Persian'},
				{'lang': 'hne', 'code': '104', 'language': 'छत्तीसगढ़ी'},
				{'lang': 'ne', 'code': '105', 'language': 'Nepali'},
				{'lang': 'mr', 'code': '106', 'language': 'Marathi'},
				{'lang': 'sa', 'code': '107', 'language': 'Sanskrit'},
				{'lang': 'hi', 'code': '108', 'language': 'Hindi'},
				{'lang': 'pa', 'code': '109', 'language': 'Punjabi'},
				{'lang': 'gu', 'code': '110', 'language': 'Gujarati'},
				{'lang': 'ta', 'code': '111', 'language': 'Tamil'},
				{'lang': 'te', 'code': '112', 'language': 'Tegulu'},
				{'lang': 'kn', 'code': '113', 'language': 'ಕನ್ನಡ'},
				{'lang': 'th', 'code': '114', 'language': 'Thai'},
				{'lang': 'yue', 'code': '115', 'language': '粵語'}
				]


def get_lang(setlang=''):
	if not setlang:
		setlang = getSetting('lang')

	try: lang = [i['lang'] for i in languagelist if i['code'] == setlang][0]
	except: lang = 'en'
	try: language = [i['language'] for i in languagelist if i['code'] == setlang][0]
	except: language = 'English'
	return lang, language

