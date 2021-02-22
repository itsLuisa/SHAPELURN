def norm(vec):
    return sum([x**2 for x in vec])**0.5
    
def dot(vec1, vec2):
    return sum([x*y for (x,y) in zip(vec1,vec2)]) 
    
def cos(vec1, vec2):
    return dot(vec1,vec2)/(norm(vec1)*norm(vec2))

# Computes two vectors from the two words and return their cosine similarity. The vectors are computed as follows: If the two word has the same letter at
# one position, both vectors get a one at this position. Otherwise vector1 get 1 at this position and vector2 -1. If one word is shorter than the other, the
# every empty position counts as if there were a different letter in this position.
def word_sim(word1,word2):
    vector1,vector2=[],[]
    if len(word1)!=len(word2):
        if len(word1) < len(word2):
            while len(word1)<len(word2):
                word1+="0"
        else:
            while len(word2)<len(word1):
                word2+="0"
           
    for w1,w2  in zip(list(word1),list(word2)):
        if w1==w2:
            vector1.append(1)
            vector2.append(1)
        else:
            vector1.append(-1)
            vector2.append(1)
    return cos(vector1,vector2)

# string is the input, the user gives, wordliste are all words, that occur in the lexicon. We test for every word in the string, whether the cosine similarity
# word_sim computes is larger than 0.65 between it and one word in the lexicon. If that is the case we assume, that the current word of the string is a word form
# of the word we already have in the lexicon. So the word is replaced by the word we have in the lexicon. The threshold 0.65 is determined experimentally an could
# be adjusted.
def sim_stemm(string,wordliste):
    stemmed = []
    for word in string.split():
        if word in wordliste:
            stemmed.append(word)
        else:
            partner = ""
            for entry in wordliste:
                if word_sim(entry,word)>0.65:
                    partner = entry
                    break
            if partner:
                print("_____stemm______:",word,partner,word_sim(partner,word))
                stemmed.append(partner)
            else:
                stemmed.append(word)            
    return " ".join(stemmed)
