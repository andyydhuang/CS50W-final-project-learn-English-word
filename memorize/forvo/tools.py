
def failed_lookup(word, settings) -> str:
    return str("<b>Definition for \"" + str(word) + "\" not found.</b><br>Check the following:<br>" +
               "- Language setting (Current: " + settings.value("target_language", 'en') + ")<br>" +
               "- Is the correct word being looked up?<br>" +
               "- Are you connected to the Internet?<br>" +
               "Otherwise, then " + settings.value("dict_source", "Wiktionary (English)") +
               " probably just does not have this word listed.")
