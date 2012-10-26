# Goal is to use nltk to detect parts of speech, then names, and then said verbs,
#    and then process the results to find when said verbs are within X words of
#    names - in those cases, the names are sources.  Want to chain the chunkers
#    together, so that said verbs are detected first, then names, then other
#    parts of speech.  This uses fallbacks, like in Packt ch. 5.  First is "said"
#    verbs, then proper names, then parts of speech (more than one, likely).
# 1) detect parts of speech across a number of articles, build up a list of 
#    verbs, look for said verbs, and make a chunker that assigns them a custom
#    tag ("JSM-SV").
# Reuters corpus is based on news articles - would be a good one to use to train
#    chunkers for this: http://text-processing.com/demo/tag/
# also check out:
# - http://streamhacker.com/2008/12/03/part-of-speech-tagging-with-nltk-part-3/

# import nltk
import nltk

# download treebank pos tagger.
nltk.download()

# try part-of-speech tagging.
# from: http://nltk.org/book/ch05.html
# tokenize sentence.
text = nltk.word_tokenize("And now for something completely different")

# tag it.
nltk.pos_tag(text)

# try a more complicated sentence:
text = nltk.word_tokenize("They refuse to permit us to obtain the refuse permit")

# tag it.
nltk.pos_tag(text)

# First, basics - tokenizing paragraphs into sentences.

# pull in an article.
from sourcenet.models import Article, Temp_Section, Newspaper

#================================================================================
# Retrieve articles in our search range.
#================================================================================

# Use Temp_Section to build up query that just gets local news for Grand Rapids Press from in-house authors over a certain date range.

# Grand Rapids Press
# first, get Newspaper Model instance for Grand Rapids Press
paper_grpress = Newspaper.objects.get( newsbank_code = "GRPB" )

# filter to just Grand Rapids Press articles
article_qs = Article.objects.filter( newspaper = paper_grpress )

# further filter to news sections.
# make instance of Temp_Status
ts_instance = Temp_Section()
ts_instance.name = Temp_Section.SECTION_NAME_ALL
article_qs = ts_instance.add_section_name_filter_to_article_qs( article_qs )

# and only in-house bylines
article_qs = article_qs.filter( Temp_Section.Q_IN_HOUSE_AUTHOR )

# now, separate query sets for before and after layoffs - Jan. 8, 2010
# before - 2009/07/01 - 2009/07/31
import datetime
date_params = {}

# start date - 2009/07/01
#date_params[ Temp_Section.PARAM_START_DATE ] = datetime.datetime( 2009, 7, 1, 0, 0, 0, 0 )
# Wants string date
date_params[ Temp_Section.PARAM_START_DATE ] = "2009-07-01"

# end date - 2009/07/31
#date_params[ Temp_Section.PARAM_END_DATE ] = datetime.datetime( 2009, 7, 31, 23, 59, 59, 99999 )
# Wants string date
date_params[ Temp_Section.PARAM_END_DATE ] = "2009-07-31"

# use it to filter to just those before layoffs.
before_qs = ts_instance.append_shared_article_qs_params( article_qs, **date_params )

# after - 2010/06/01 - 2010/06/30
date_params = {}

# start date - 2010/06/01
date_params[ Temp_Section.PARAM_START_DATE ] = "2010-06-01"

# end date - 2010/06/30
date_params[ Temp_Section.PARAM_END_DATE ] = "2010-06-30"

# use it to filter to just those before layoffs.
after_qs = ts_instance.append_shared_article_qs_params( article_qs, **date_params )

# Need to start experimenting with chunkers.
# In packt book, NER is on page 133.

# get first article in before list.
test_article = before_qs[ 0 ]

# get article's text...
article_text_qs = test_article.article_text_set.all()
article_text = article_text_qs[ 0 ].content

# * todo: Strip dateline from beginning.

#================================================================================
# NLTK stuff
#================================================================================

#--------------------------------------------------------------------------------
# Tokenizing
#--------------------------------------------------------------------------------

# Now to NLTK: first, break out into sentences.
from nltk.tokenize import sent_tokenize
sentences_list = sent_tokenize( article_text )

# If you are going to tokenize lots of paragraphs (as we are), load the pickled
#    tokenizer and re-use it.
import nltk
import nltk.data
sentence_tokenizer = nltk.data.load( 'tokenizers/punkt/english.pickle' )

# tokenize using the tokenize() method.
sentence_list = sentence_tokenizer.tokenize( article_text )

# grab a sample sentence
sentence = sentence_list[ 0 ]

# tokenize it.
# one-off method call:
#from nltk.tokenize import word_tokenize
#word_tokenize('Hello World.')

# load pickled tokenizer
from nltk.tokenize import TreebankWordTokenizer
tokenizer = TreebankWordTokenizer()
word_list = tokenizer.tokenize( sentence )

#--------------------------------------------------------------------------------
# Parts of Speech
#--------------------------------------------------------------------------------

# Default tagging
from nltk.tag import DefaultTagger

# if all else fails, make an unknown word a noun ( "NN" )
default_tagger = DefaultTagger( 'NN' )

# try it.
tagged_sentence = default_tagger.tag( word_list )

# Can also batch tag, but need a list of sentences, each already tokenized.
#tagger.batch_tag([['Hello', 'world', '.'], ['How', 'are', 'you', '?']])

#--------------------------------------------------------------------------------
# Training taggers
#--------------------------------------------------------------------------------

# so far so good.  Next have to train taggers.

# Unigram, training on Treebank corpus
from nltk.tag import UnigramTagger
from nltk.corpus import treebank
train_sents = treebank.tagged_sents()[:3000]
unigram_tagger = UnigramTagger(train_sents)

# try it on our word_list.
unigram_tagger.tag( word_list )

# Backoff taggers - hierarchy of taggers, first tags all it can, then next takes
#    a stab at all with tag of None, then next, etc.

# Unigram with Default as backoff:
train_sents = treebank.tagged_sents()
unigram_tagger = UnigramTagger( train_sents, backoff = default_tagger )

# Add in contextual taggers:
# - bigram - current word plus previous token.
# - trigram - current word plus previous two tokens.
from nltk.tag import BigramTagger, TrigramTagger
bitagger = BigramTagger( train_sents )
tritagger = TrigramTagger( train_sents )

# function to chain taggers together - either make a NLTK helper class, or find
#    the code file where this came from (tag_util.py).
def backoff_tagger( train_sents, tagger_classes, backoff=None ):
    for cls in tagger_classes:
        backoff = cls( train_sents, backoff = backoff )
    return backoff
#-- END poorly written backoff chainer function --#

# chain taggers together
combined_tagger = backoff_tagger( train_sents, [ UnigramTagger, BigramTagger, TrigramTagger ], backoff = default_tagger )

# try it out.
tagged_words = combined_tagger.tag( word_list )

# todo: try out the other fancier methods for training a tagger: Brill Tagger,
#    Classifier-based tagging.

# todo: use names to train a name tagger.

# todo: tie all these classifiers together, see which does the best for named
#   entity chunking.

#--------------------------------------------------------------------------------
# Pickling Trained taggers
#--------------------------------------------------------------------------------

import pickle

# persist tagger to file system
f = open('tagger.pickle', 'w')
pickle.dump(tagger, f)
f.close()

# load tagger from storage
f = open( 'tagger.pickle', 'r' )
tagger = pickle.load( f )

# If your tagger pickle file is located in a NLTK data directory, you could also
#    use nltk.data.load('tagger.pickle')

#--------------------------------------------------------------------------------
# Named Entity Chunking
#--------------------------------------------------------------------------------

# Once you have parsed parts of speech from your sentences, then you can look
#    for names.  Must pass the ne_chunk method a list of tagged words, though,
#    not just a list of tokens.
from nltk.chunk import ne_chunk
ne_chunk( tagged_words )

# todo: figure out how to deal with the output of chunker for named-entity
#    recognition.

# todo: figure out how to detect, filter said verbs - need to go through
#    articles, find all said verbs, make a custom classifier that can tag them
#    differently.

# todo: need a way to take said verbs and proper names and see if they are
#    proximal in a given sentence - if not within 4 or 5 words, might not be
#    attribution.