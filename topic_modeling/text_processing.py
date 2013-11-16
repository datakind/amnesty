# -*- coding: utf-8 -*-
from gensim import corpora
from nltk.stem import LancasterStemmer, PorterStemmer, SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, wordpunct_tokenize
from string import punctuation
from HTMLParser import HTMLParser
import re

# load in custom stopwords
stopwords = [w.strip() for w in open('stopwords.txt').read().split('\n') if w != '']

# html stripping
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    raw_text = s.get_data()
    raw_text = re.sub(r'\n|\t', ' ', raw_text)
    return re.sub('\s+', ' ', raw_text).strip()

def remove_non_ascii(string):
  """
  Remove all non-ascii characters from input string
  """
  return ''.join(character for character in string if ord(character)<128)

def remove_URLs(string):
  """
  Remove all URLs from input string
  """
  pattern = r'((http|ftp|https):\/\/)?[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?'
  return re.sub(pattern, ' ', string)

def clean_text(
      text, 
      html=False, 
      digits=False, 
      urls=False, 
      ascii=False
  ):
  """
  Remove html, digits, weird white space, URLs, non-ascii chars from raw text
  """
  # text is none, return an empty string
  if text is None:
    return ''

  if html is False:
    # strip html markup
    text = strip_tags(text)

  if digits is False:
    # remove digits
    text = re.sub(r'\d', ' ', text)

  if urls is False:
    # remove all urls
    text = remove_URLs(text)

  if ascii is False:
    # remove all non-ascii characters
    text = remove_non_ascii(text)

  # standardize white space
  text = re.sub(r'\s+', ' ', text) 

  # return 
  return text

def tokenize_and_normalize_text(
      text,
      wordpunct=True,
      filter_stopwords=True,
      normalizer='wordnet',
      lang='english'
  ):
  """
  Remove stopwords, bare punctuation, capitalization; lemmatize or stem words

  Parameters
  ----------
  text : string
    a single string of words and punctuation, a "text"
  filter_stopwords : boolean (default True)
    if True, filter out stopwords in nltk.corpus.stopwords
  normalizer : string or None (default 'wordnet')
    if 'wordnet', lemmatizes words
    if in ['porter', 'lancaster', 'snowball'], stems words
    if None, doesn't normalize words
  lang : string (default 'english')
    language to use for stopwords and snowball stemmer

  Returns
  -------
  norm_words : list of strings
    list of normalized words comprising text
  """

  # check input
  if not isinstance(text, basestring):
    print '**WARNING: text is not a string!'
    return None

  # check stopwords arg
  if lang not in stopwords.fileids():
    print '***ERROR: lang', lang, 'not in', stopwords.fileids(), '!'
    return None
  stops = frozenset(stopwords)

  # toxenize words
  if wordpunct is True:
    words = wordpunct_tokenize(text.lower())
  else:
    words = word_tokenize(text.lower())

  # remove stopwords
  if filter_stopwords is True:
    good_words = (word for word in words
            if not all([char in punctuation for char in word])
            and len(word) > 0 and len(word) < 25
            and word not in stops)
  else:
    good_words = (word for word in words
            if not all([char in punctuation for char in word])
            and len(word) > 0 and len(word) < 25)

  # normalize text
  normalizers = ['wordnet', 'porter', 'lancaster', 'snowball']
  if normalizer == 'wordnet':
    lemmatizer = WordNetLemmatizer()
    norm_words = [lemmatizer.lemmatize(word) for word in good_words]
  elif normalizer in ['porter', 'lancaster', 'snowball']:
    if normalizer == 'porter':
      stemmer = PorterStemmer()
    elif normalizer == 'lancaster':
      stemmer = LancasterStemmer()
    elif normalizer == 'snowball':
      if lang not in SnowballStemmer.languages:
        print '***ERROR: lang', lang, 'not in', SnowballStemmer.languages, '!'
        return None
      stemmer == SnowballStemmer(lang)
    norm_words = [stemmer.stem(word) for word in good_words]
  elif normalizer is None:
    norm_words = good_words
  else:
    print '***ERROR: normalizer', normalizer, 'not in', normalizers, '!'
    return None

  return norm_words

def remove_infrequent_words(texts, min_freq=2):
  # count words across all corpora
  counts = {}
  for text in texts:
    for word in text:
      if counts.has_key(word):
        counts[word] += 1
      else:
        counts[word] = 1

  # filter out infrequent words    
  cleaned_texts = [] 
  for text in texts:
    cleaned_text = []
    for word in text:
      if counts[word] >= min_freq:
        cleaned_text.append(word)

    # reconstruct texts
    cleaned_texts.append(cleaned_text)

  # return
  return cleaned_texts

def process_texts(texts, **kwargs):
  """
  Given a list of texts, cleans and normalizes text then
  returns a dictionary of word<->ID mappings
  and a corpus of sparse vectors of bag-of-word-IDs
  """
  # ensure that texts is a list
  if isinstance(texts, basestring):
    texts = [texts]

  # parse args
  filter_stopwords = kwargs.get('filter_stopwords', True)
  normalizer = kwargs.get('normalizer', 'porter')
  lang = kwargs.get('lang', 'english')
  rm_infrequent = kwargs.get('rm_infrequent', True)
  min_freq = kwargs.get('min_freq', 2)

  # clean texts
  cleaned_texts = [clean_text(t) for t in texts]

  # normalize texts
  normed_texts = [
    tokenize_and_normalize_text(
      text=t, 
      filter_stopwords=filter_stopwords,
      normalizer = normalizer,
      lang=lang
    )
    for t in cleaned_texts
  ]

  # remove infrequent words
  if rm_infrequent:
    normed_texts = remove_infrequent_words(
      texts = normed_texts, 
      min_freq = min_freq
    )

  # convert to gensim corpus and dictionary
  id2word = corpora.Dictionary(normed_texts)
  corpus = [id2word.doc2bow(text) for text in normed_texts]

  # return
  return corpus, id2word
