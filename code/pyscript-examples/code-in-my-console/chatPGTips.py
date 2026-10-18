from monkeyAnswers import *
from random import random, randrange, seed
#from random import gauss       # MicroPython doesn't have gauss, so we do this ourselves below
import time
import sys

# Basic example used for demo purposes - lacking some basic error checking etc.

# Question types
# Note: need a function of matching name (and list in imported monkeyAnswers) for each entry in treatQuestionTypesAs
questionTypes =         ["who", "what", "where", "why", "when", "how"]
treatQuestionTypesAs =  questionTypes.copy()
questionTypes +=        ["which"]
treatQuestionTypesAs += ["what"]                            # I.e. treat "which" like "what"
questionTypes +=        ["whom", "whose"]
treatQuestionTypesAs += ["who"]*2                           # I.e. treat "whom" and "whose" like "who"
decideQuestions =       ["is", "isn't", "has", "hasn't", "should", "shouldn't", "have", "haven't", 
                         "could", "couldn't", "will", "won't", "can", "can't"]
#decideQuestions +=      ["if"]     # Not sure about this one
questionTypes +=        decideQuestions
treatQuestionTypesAs += ["decide"]*len(decideQuestions)     # I.e. treat all decideQuestions as "decide"
defaultQuestionType =   "unsure"

# We do this ourselves as MicroPython random doesn't have gauss
import math
def gauss(mu=0.0, sigma=1.0):
    # Box-Muller transform
    u1 = random()
    u2 = random()
    # Avoid log(0)
    while u1 == 0: u1 = random()
    # Normalised result
    z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    # return mu, sigma adjusted output
    return mu + sigma * z0

class chatPGTips:
    
    '''
    Class to generate answers based on a pre-made bank of options (in monkeyAnswers.py)
    Inspired by MATLAB "why", chatGPT, and of course PG Tips!
    Try:

    >>> from chatPGTips import chatPGTips
    >>> monkey = chatPGTips()
    >>> monkey.ask("What is the answer to my question monkey?")
    
    Optional arguments on init include:
    
    deterministic   (bool)  If typed questions are deterministic            (default = False)
    print           (bool)  Whether to print the answer                     (default = True)
    typeMode        (bool)  Whether or not to print using simulated typing  (default = True)
    question        (str)   Whether to immediately ask a question           (default = None)

    Other ways of calling include:

    >>> monkey.who()
    >>> monkey.how()
    >>> monkey.when()
    >>> monkey.surpriseMe()
    etc...

    '''
    
    def __init__(self, deterministic=False, print=True, typeMode=True, question=None):
        
        # Whether or not we attempt to make (typed) answers deterministic
        self.deterministic = deterministic
        # Whether or not to print the result, or just store
        self.print = print
        # If self.print == True, whether or not to print using typing style (i.e. one character at a time)
        self.typeMode = typeMode
        # We start with no answer
        self.answer = None
        # If given an input question, ask the question straight away
        if not question is None:
            self.ask(question)
    
    def ask(self, question):
        
        '''
        Ask a question - e.g. .ask("Tell me why")
        '''
        
        # Look for question type
        (questionType, questionIndex) = self.__getQuestionType__(question, questionTypes)
        # An then...
        if not questionType is None:
            # If found question type, get how we treat it
            questionType = treatQuestionTypesAs[questionIndex]
        else:
            # Use default question type
            qType = defaultQuestionType
        # If process is deterministic...
        if self.deterministic:
            # Attempt to set the seed of the random number generator based on the question
            # (i.e. it's sum of it's ascii characters)
            qSum = 0
            for x in list(question):
                qSum += ord(x)
            seed(qSum)
        # Ask the question!!
        getattr(self, qType)()
    
    def who(self):
        '''
        Respond to "who" question
        '''
        # Ask me who
        self.__respond__(self.__getAnswer__(whoList))
    
    def what(self):
        '''
        Respond to "what" question
        '''
        # Ask me what
        self.__respond__(self.__getAnswer__(whatList))
    
    def where(self):
        '''
        Respond to "where" question
        '''
        # Ask me where
        self.__respond__(self.__getAnswer__(whereList))
    
    def why(self):
        '''
        Respond to "why" question
        '''
        # Ask me why
        self.__respond__(self.__getAnswer__(whyList))
    
    def when(self):
        '''
        Respond to "when" question
        '''
        # Ask me when
        self.__respond__(self.__getAnswer__(whenList))
    
    def how(self):
        '''
        Respond to "how" question
        '''
        # Ask me how
        self.__respond__(self.__getAnswer__(howList))
        
    def decide(self):
        '''
        Respond to "decide" question 
        '''
        self.__respond__(self.__getAnswer__(decideList))
        
    def unsure(self):
        '''
        Respond to question to which I am "unsure"
        '''
        self.__respond__(self.__getAnswer__(unsureList))
        
    def surpriseMe(self):
        '''
        Ask me for a completely random type of answer
        '''
        # Ask a random question of any type
        uniqueQuestionTypes = list(set(treatQuestionTypesAs))
        qTypes = uniqueQuestionTypes+[defaultQuestionType]
        qType = self.getRandomEntry(qTypes)
        getattr(self, qType)()
    
    def getRandomEntry(self, x):
        '''
        Internal
        Get random item from list/dict
        '''
        # If dict or not list
        if isinstance(x, dict):
            # Make dict in to list
            x = list(x.keys())
        elif not isinstance(x, list):
            return x
        # Number if items in list
        numItems = len(x)
        # If list has items
        if numItems > 0:
            # Get random item
            randn = randrange(0, numItems)
            xItem = x[randn]
        else:
            # No items
            xItem = None
        return xItem
    
    def __getQuestionType__(self, question, questionTypes):
        '''
        Internal
        Get a question type based on a user question
        '''
        # Attempt to find the question type
        if isinstance(question, str):
            # If question is a string...
            # Make lower case
            question = question.lower()
            # Length of question
            questionLength = len(question)
            # Index of start of a question - initial value (i.e. not found)
            firstQuestionIndex = questionLength
            # No questions found yet
            firstQuestionType = None
            # Loop round question types (except for last one)...
            for i, qType in enumerate(questionTypes):
                # Index of question type in question (returns -1 if not found)
                qIndex = question.find(qType)
                # If found question type in question, and is before any prev types found
                if qIndex >= 0 and qIndex < firstQuestionIndex:
                    # Current found question type and index
                    firstQuestionType = i
                    firstQuestionIndex = qIndex
            # This should mean we have a question
            if not firstQuestionType is None:
                questionType = questionTypes[firstQuestionType]
            else:
                questionType = None
            # Return result
            return (questionType, firstQuestionIndex)
    
    def __getAnswer__(self, x):
        
        '''
        Internal
        Get a random answer from list/dict structure
        This function has got incredibly messy, 
        but it kind of works when you know what you're doing so it is what it is!
        '''
        
        # Initial empty answer
        ans = ""
        # Assume list at the start is a set of options to use
        x = self.getRandomEntry(x)
        # Loop round for as long as we still have a list or dict
        while isinstance(x, dict) or isinstance(x, list):
            if isinstance(x, dict):
                # Get random key (which is also a string to append)
                appendOpt = self.getRandomEntry(x)
                # depending on result...
                if appendOpt is None:
                    # We have nothing to append anymore
                    xNext = None
                    appendOpt = ""
                else:
                    # Contents are next loops possible answers
                    xNext = x[appendOpt]
            elif isinstance(x, list):
                # Nothing to add unless find otherwise
                appendOpt = ""
                # make a copy of current list
                xNext = x.copy()
                # Get options list
                if all(isinstance(val, str) for val in xNext):
                    # If all items are strings, then options are the current list
                    appendOpts = xNext
                    xNext = None
                else:
                    # Otherwise, options are first item in list
                    # (and remainder of list is future options)
                    appendOpts = xNext.pop(0)
                # Get append option and object for next loop 
                if isinstance(appendOpts, dict):
                    # If options are a dict then keep for next loop
                    xNext = appendOpts
                else:
                    # Otherwise get random item from list
                    opt = self.getRandomEntry(appendOpts)
                    if not opt is None:
                        # If we find something...
                        if isinstance(opt, str):
                            # Option is a string if we get one
                            appendOpt = opt
                        else:
                            # otherwise  
                            xNext = opt.copy()
            # Next loops possible answers
            x = xNext
            # Add to answer (if we have something to add)...
            if len(appendOpt) > 0:
                if len(ans) == 0:
                    # If this is the start
                    # Make sure we start the question with a capital letter
                    asList = list(appendOpt)
                    asList[0] = asList[0].upper()
                    appendOpt = "".join(asList)
                else:
                    # If not at the start...
                    # Strip trailing spaces
                    ans = ans.strip()
                    # If a new sentence then start with a capital letter
                    if any(ans[-1]==endText for endText in [".", "?", "!"]):
                        asList = list(appendOpt)
                        asList[0] = asList[0].upper()
                        appendOpt = "".join(asList)
                    # include space if new text doesn't start with punctuation or space
                    if not any(appendOpt[0]==endText for endText in [" ", "'", ",", ".", "?", "!"]):
                        ans += " "
                # Add to answer
                ans += appendOpt
        # Delete any leading/trailing spaces if got any by mistake
        ans = ans.strip()
        # Stick a full stop on if we don't have a final punctuation mark.
        if len(ans) > 0 and not any(ans[-1]==endText for endText in [".", "?", "!"]):
            ans += "."
        # And that's your answer!
        return ans
    
    def __respond__(self, answer):
        
        '''
        Internal
        Respond to the question
        '''        
        # Store the answer
        self.answer = answer
        # If printing...
        if self.print:
            if not self.typeMode:
                # If not typing, just print to console
                print(self.answer)
            else:
                # If typing response...
                for char in answer: 
                    pauseTime = abs(gauss())*0.06
                    time.sleep(pauseTime)
                    sys.stdout.write(char)
                    sys.stdout.flush()
                print('')

