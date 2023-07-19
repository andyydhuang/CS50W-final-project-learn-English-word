from .constants import LookUpResults
from .dictionary import *
from .tools import *
from PyQt5.QtCore import *
settings = QSettings("CS50Web", "Final")

class DictObject():
    def __init__(self) -> None:
        self.settings = settings

    def getLanguage(self) -> str:
        return self.settings.value("target_language", "en")  # type: ignore

    def getLemGreedy(self) -> bool:
        return self.settings.value("lem_greedily", False, type=bool)  # type: ignore

    def lookup(self, word: str, use_lemmatize: bool) -> LookUpResults:
        """
        Look up a word and return a dict with the lemmatized form (if enabled)
        and definition
        """
        word = re.sub('[«»…,()\\[\\]_]*', "", word)
        # TODO
        # why manually check "lemmatization" in settings when you can pass it through parameter?
        lemmatize = use_lemmatize and self.settings.value(
            "lemmatization", True, type=bool)
        lem_greedily = self.getLemGreedy()
        lemfreq = self.settings.value("lemfreq", True, type=bool)
        short_sign = "Y" if lemmatize else "N"
        language = self.getLanguage()
        TL = language  # Handy synonym
        gtrans_lang: str = self.settings.value("gtrans_lang", "en")
        dictname: str = self.settings.value("dict_source", "Wiktionary (English)")
        freqname: str = self.settings.value("freq_source", "<disabled>")
        if freqname != "<disabled>":
            freq_found = False
            freq_display = self.settings.value("freq_display", "Rank")
            try:
                freq, max_freq = getFreq(word, language, lemfreq, freqname)
                freq_found = True
            except TypeError:
                pass

            if freq_found:
                if freq_display == "Rank":
                    self.freq_display.setText(f'{str(freq)}/{str(max_freq)}')
                elif freq_display == "Stars":
                    self.freq_display.setText(freq_to_stars(freq, lemfreq))
            else:
                if freq_display == "Rank":
                    self.freq_display.setText('-1')
                elif freq_display == "Stars":
                    self.freq_display.setText(freq_to_stars(1e6, lemfreq))
        #self.status(
        #    f"L: '{word}' in '{language}', lemma: {short_sign}, from {dictionaries.get(dictname, dictname)}")
        if dictname == "<disabled>":
            word = lem_word(word, language, lem_greedily) if lemmatize else word
            self.status("Dict disabled")
            return {
                "word": word,
                "definition": ""
            }
        try:
            item = lookupin(
                word,
                language,
                lemmatize,
                lem_greedily,
                dictname,
                gtrans_lang,
                self.settings.value("gtrans_api", "https://lingva.ml"))
        except Exception as e:
            item = {
                "word": word,
                "definition": failed_lookup(word, self.settings)
            }
            return item
        dict2name = self.settings.value("dict_source2", "<disabled>")
        if dict2name == "<disabled>":
            return item
        try:
            item2: LookUpResults = lookupin(
                word,
                language,
                lemmatize,
                lem_greedily,
                dict2name,
                gtrans_lang)
        except Exception as e:
            self.status("Dict-2 failed" + repr(e))
            self.definition2.clear()
            return item

        return {
            "word": item['word'],
            'definition': item['definition'],
            'definition2': item2['definition']}

    def lookupAudio(self, word: str):
        self.audio_path = ""

        if self.settings.value("audio_dict", "Forvo (all)") == "<disabled>":
            return

        try:
            self.audios = getAudio(
                word,
                self.settings.value("target_language", 'en'),
                dictionary=self.settings.value("audio_dict", "Forvo (all)"),
                custom_dicts=json.loads(
                    self.settings.value("custom_dicts", '[]')))
        except Exception:
            self.audios = {}

        return self.audios