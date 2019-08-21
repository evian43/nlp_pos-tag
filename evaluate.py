import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "libs")))
import getopt

def addTuples(tuple1, tuple2):
   return tuple([tuple1[i]+tuple2[i] for i in range(len(tuple1))])

def addListToList(list1, list2):
   for i in range(len(list1)):
      list1[i] += list2[i]


def subtractListFromList(list1, list2):
   for i in range(len(list1)):
      list1[i] -= list2[i]


def dotProduct(list1, list2):
   nReturn = 0
   for i in range(len(list1)):
      nReturn += list1[i] * list2[i]
   return nReturn


def addDictToDict(dict1, dict2):
   for key in dict2:
      if key in dict1:
         dict1[key] += dict2[key]
      else:
         dict1[key] = dict2[key]

def subtractDictFromDict(dict1, dict2):
   for key in dict2:
      if key in dict1:
         dict1[key] -= dict2[key]
      else:
         dict1[key] = -dict2[key]

class CRawSentenceReader(object):

   def __init__(self, sPath, sEncoding="utf-8"):
      self.m_sPath = sPath
      self.m_oFile = open(sPath)
      self.m_sEncoding = sEncoding

   def __del__(self):
      self.m_oFile.close()

   def readNonEmptySentence(self):
      # 1. read one line
      sLine = "\n"                              # use a pseudo \n to start
      while sLine:                              # while there is a line
         sLine = sLine.strip()                  # strip the line
         if sLine:                              # if the line isn't empty
            break                               # break
         sLine = self.m_oFile.readline()        # read next line
         if not sLine:                          # if eof symbol met
            return None                         # return
      # 2. analyse this line
      uLine = sLine.decode(self.m_sEncoding)    # find unicode
      lLine = [sCharacter.encode(self.m_sEncoding) for sCharacter in uLine]
      return lLine


   def readSentence(self):
      # 1. read one line
      sLine = self.m_oFile.readline()           # read next line
      if not sLine:                             # if eof symbol met
         return None                            # return
      # 2. analyse this line
      uLine = sLine.strip().decode(self.m_sEncoding)    # find unicode
      lLine = [sCharacter.encode(self.m_sEncoding) for sCharacter in uLine]
      return lLine


class CPennTaggedSentenceReader(object):

   def __init__(self, sPath):
      self.m_sPath = sPath
      self.m_oFile = open(sPath)

   def __del__(self):
      self.m_oFile.close()

   def readNonEmptySentence(self, bIgnoreNoneTag):
      # 1. read one line
      sLine = "\n"                              # use a pseudo \n to start
      while sLine:                              # while there is a line
         sLine = sLine.strip()                  # strip the line
         if sLine:                              # if the line isn't empty
            break                               # break
         sLine = self.m_oFile.readline()        # read next line
         if not sLine:                          # if eof symbol met
            return None                         # return
      # 2. analyse this line
      lLine = sLine.strip().split(" ")
      lNewLine = []
      for nIndex in range(len(lLine)):
         tTagged = tuple(lLine[nIndex].split("_"))
         assert(len(tTagged)<3)
         if len(tTagged)==1:
            tTagged = (tTagged[0], "-NONE-")
         if (bIgnoreNoneTag==False) or (tTagged[0]): # if we take -NONE- tag, or if we find that the tag is not -NONE-
            lNewLine.append(tTagged)
      return lNewLine

   def readSentence(self, bIgnoreNoneTag):
      # 1. read one line
      sLine = self.m_oFile.readline()           # read next line
      if not sLine:                             # if eof symbol met
         return None                            # return
      # 2. analyse this line
      lLine = sLine.strip().split(" ")
      lNewLine = []
      for nIndex in range(len(lLine)):
         tTagged = tuple(lLine[nIndex].split("_"))
         assert(len(tTagged)<3)
         if len(tTagged)==1:
            tTagged = (tTagged[0], "-NONE-")
         if (bIgnoreNoneTag==False) or (tTagged[0]): # if we take -NONE- tag, or if we find that the tag is not -NONE-
            lNewLine.append(tTagged)
      return lNewLine


def evaluateSentence(lCandidate, lReference):
   nCorrectWords = 0
   nCorrectTags = 0
   nChar = 0
   indexCandidate = 0
   indexReference = 0
   while lCandidate and lReference:
      if lCandidate[0][0] == lReference[0][0]:  # words right
         nCorrectWords += 1
         if lCandidate[0][1] == lReference[0][1]: # tags
            nCorrectTags += 1
         indexCandidate += len(lCandidate[0][0]) # move
         indexReference += len(lReference[0][0])
         lCandidate.pop(0)
         lReference.pop(0)
      else:
         if indexCandidate == indexReference:
            indexCandidate += len(lCandidate[0][0]) # move
            indexReference += len(lReference[0][0])
            lCandidate.pop(0)
            lReference.pop(0)
         elif indexCandidate < indexReference:
            indexCandidate += len(lCandidate[0][0])
            lCandidate.pop(0)
         elif indexCandidate > indexReference:
            indexReference += len(lReference[0][0]) # move
            lReference.pop(0)
   raw_l = max(indexCandidate, indexReference)
   total_num = (raw_l + 1) * raw_l / 2
   return nCorrectWords, nCorrectTags, total_num


def evaluateSentence_boundaries(lCandidate, lReference):
   nCorrectWords = 0
   nCorrectTags = 0
   indexCandidate = 0
   indexReference = 0
   while len(lCandidate) > 1 and len(lReference) > 1:
      if lCandidate[0][0] == lReference[0][0]:  # words right
         nCorrectWords += 1
         if lCandidate[0][1] == lReference[0][1] and lCandidate[1][1] == lReference[1][1]: # tags
            nCorrectTags += 1
         indexCandidate += len(lCandidate[0][0]) # move
         indexReference += len(lReference[0][0])
         lCandidate.pop(0)
         lReference.pop(0)
      else:
         if indexCandidate == indexReference:
            nCorrectTags += 1
            if lCandidate[0][1] == lReference[0][1] and lCandidate[1][1] == lReference[1][1]:  # tags
                nCorrectTags += 1
            indexCandidate += len(lCandidate[0][0]) # move
            indexReference += len(lReference[0][0])
            lCandidate.pop(0)
            lReference.pop(0)
         elif indexCandidate < indexReference:
            indexCandidate += len(lCandidate[0][0])
            lCandidate.pop(0)
         elif indexCandidate > indexReference:
            indexReference += len(lReference[0][0]) # move
            lReference.pop(0)
   return nCorrectWords, nCorrectTags


def readNonEmptySentenceList(sents, bIgnoreNoneTag=True):
    out = []
    for sent in sents:
        lNewLine = []
        lLine = sent.split(' ')
        for nIndex in range(len(lLine)):
            if len(lLine[nIndex])==0:
                continue
            if lLine[nIndex][0]=='/':
                tTagged=('/',lLine[nIndex][-1])
            else:
                tTagged = tuple(lLine[nIndex].split("/"))
            if len(tTagged)>2:
                tTagged=(tTagged[0],tTagged[-1])
            assert (len(tTagged) < 3)
            if len(tTagged) == 1:
                tTagged = (tTagged[0], "-NONE-")
            if (bIgnoreNoneTag == False) or (tTagged[0]):  # if we take -NONE- tag, or if we find that the tag is not -NONE-
                lNewLine.append(tTagged)
        out.append(lNewLine)
    return out


def score(sReference, sCandidate, tag_num=1, verbose=False):
    nTotalCorrectWords = 0
    nTotalCorrectTags = 0
    nTotalPrediction = 0
    nCandidateWords = 0
    nReferenceWords = 0
    reference = readNonEmptySentenceList(sReference)
    candidate = readNonEmptySentenceList(sCandidate)
    assert len(reference) == len(candidate)
    for lReference, lCandidate in zip(reference, candidate):
        n = len(lCandidate)
        nCandidateWords += len(lCandidate)
        nReferenceWords += len(lReference)
        nCorrectWords, nCorrectTags, total = evaluateSentence(lCandidate, lReference)
        nTotalCorrectWords += nCorrectWords
        nTotalCorrectTags += nCorrectTags
        nTotalPrediction += total
    word_precision = float(nTotalCorrectWords) / float(nCandidateWords)
    word_recall = float(nTotalCorrectWords) / float(nReferenceWords)
    tag_precision = float(nTotalCorrectTags) / float(nCandidateWords)
    tag_recall = float(nTotalCorrectTags) / float(nReferenceWords)
    word_false_negative = nCandidateWords - nTotalCorrectWords
    tag_false_negative = nCandidateWords - nTotalCorrectTags
    word_real_negative = nTotalPrediction - nReferenceWords
    tag_real_negative = nTotalPrediction * tag_num - nReferenceWords
    word_tnr = 1 - float(word_false_negative) / float(word_real_negative)
    tag_tnr = 1 - float(tag_false_negative) / float(tag_real_negative)
    if word_precision + word_recall > 0:
        word_fmeasure = (2 * word_precision * word_recall) / (word_precision + word_recall)
    else:
        word_fmeasure = 0.00001

    if tag_precision + tag_recall == 0:
        tag_fmeasure = 0.0
    else:
        tag_fmeasure = (2 * tag_precision * tag_recall) / (tag_precision + tag_recall)
    if verbose:
        return word_precision, word_recall, word_fmeasure, tag_precision, tag_recall, tag_fmeasure, word_tnr, tag_tnr
    else:
        return word_fmeasure, tag_fmeasure


def score_boundaries(sReference, sCandidate, verbose=False):
    nTotalCorrectWords = 0
    nTotalCorrectTags = 0
    nCandidateWords = 0
    nReferenceWords = 0
    reference = readNonEmptySentenceList(sReference)
    candidate = readNonEmptySentenceList(sCandidate)
    assert len(reference) == len(candidate)
    for lReference, lCandidate in zip(reference, candidate):
        n = len(lCandidate)
        nCandidateWords += len(lCandidate) - 1
        nReferenceWords += len(lReference) - 1
        nCorrectWords, nCorrectTags = evaluateSentence_boundaries(lCandidate, lReference)
        nTotalCorrectWords += nCorrectWords
        nTotalCorrectTags += nCorrectTags
    word_precision = float(nTotalCorrectWords) / float(nCandidateWords)
    word_recall = float(nTotalCorrectWords) / float(nReferenceWords)
    tag_precision = float(nTotalCorrectTags) / float(nCandidateWords)
    tag_recall = float(nTotalCorrectTags) / float(nReferenceWords)
    if word_precision + word_recall > 0:
        word_fmeasure = (2 * word_precision * word_recall) / (word_precision + word_recall)
    else:
        word_fmeasure = 0.00001

    if tag_precision + tag_recall == 0:
        tag_fmeasure = 0.0
    else:
        tag_fmeasure = (2 * tag_precision * tag_recall) / (tag_precision + tag_recall)
    if verbose:
        return word_precision, word_recall, word_fmeasure, tag_precision, tag_recall, tag_fmeasure
    else:
        return word_fmeasure, tag_fmeasure


if __name__ == '__main__':
    #refs is the ground truth pos data, cads is the candidate generated by your model.
    refs=open('data/pre_pos/pos_crf_100.txt',encoding='utf-8').readlines()
    output=[]
    cads=open('data/pre_pos/test_pos.txt',encoding='utf-8').readlines()
    word_precision, word_recall, word_fmeasure, tag_precision, tag_recall, tag_fmeasure, word_tnr, tag_tnr=score(refs,cads,verbose=True)

    #print("Word precision:", word_precision)
    #print("Word recall:", word_recall)
    print("Tag precision:", tag_precision)
    print("Tag recall:", tag_recall)
    #print("Word F-measure:", word_fmeasure)
    print("Tag F-measure:",  tag_fmeasure)

