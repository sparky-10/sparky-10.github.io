# Lists/dicts to make random answers

'''
I'm not going to comment this particularly well as it's complicated, and evolved a mind of it's own!!
'''

# Sentence constructors
skip = ""
stop = ["."]
quiz = ["?"]
prefix = ["monkey thinks", "monkey says", "I bet", "i'm pretty sure", "I've checked with Google and",
          "you know I think", "odds are", "I'd bet my house that", "if in doubt", "if all else fails"]
prefixQuestion = ["could it be that", "do you reckon", "are you sure"]
prefixByTry = ["Should you try", "Could your mum help by", "Would you consider"]
itIs = ["it's", "it is", "it isn't", "it is not", "that's"]
prefixAdverb = ["likely", "probably", "possibly", "mainly", "predominantly", "definitely", "mostly", "usually", "largely", "briefly", 
                "objectively", "vaguely", "obligingly", "fastidiously", "maybe", "absolutely"]
identity = ["the butler", "a monkey", "Johnny Vegas", "a badger", "my mum", "Elvis", "the Tipps family",
                   "Hugh Hefner", "Dick Van Dyke", "Jane McDonald", "the real Father Christmas", "the Pope",
                   "Princess Diana", "Big Bird from Sesame Street", "that bloke you once had a pint with", "Chris Waddle"]
doing = ["riding a unicycle", "dancing the tango", "slowly waving", "desperately running to catch a bus", "furiously tap dancing", 
         "roller skating", "drinking their morning brew", "tickling a monkey", "poking Johnny Vegas", "putting the kettle on", 
         "making a fresh pot of tea", "pushing a wheelbarrow", "whittling wood", "slicing onions in to tiny pieces", "smoking my cigars", 
         "reciting poetry"]
wearing = ["wearing a", "dressed in a", "sporting a", "showing off their new", "donned in a"]
adjective = ["over-sized", "smart", "dapper", "vintage", "scruffy", "rather tight", "splendid", "expensive", "moth eaten", "somewhat stained",
             "tiny", "ancient", "'leaves nothing to the imagination'", "inappropriate", "bright", "shiny", "sequin covered", "Sunday best",
             "dour", "kinky", "homemade", "sensible", "overdue a wash", "sorry excuse for a", "fetching"]
colour = ["red", "electric pink", "beige", "blue", "mint green", "off-white", "luminous yellow", "tangerine", "mauve"]
clothes = ["pair of hot pants", "pair of stilettos", "jacket", "top hat", "pair of shoes", "Hawaiian shirt", "pair of flares", 
            "beret", "pencil skirt", "pair of cycling shorts", "pair of knee high hiking socks", "pair of fat pants", 
            "set of pyjamas", "giant monkey costume"]
pairedWith = ["and matching bow tie", "and giant ski goggles", "with a smashing blouse", "and polka-dot underpants", "and dressing gown"]
whilstPrefix = ["whilst", "while", "and", "while also", "and simultaneously", "and at the same time", 
                "and displaying their multitasking skills by also"]
whilst = ["learning French", "eating their breakfast", "walking backwards", "deciding what's for dinner", "doing star jumps",
          "winning first prize at the village annual vegetable growing competition", "moving like Jagger", "walking the walk", "talking the talk",
          "just living for the moment", "shouting YOLO at the top of their voice", "eating a cheese sandwich in a car park", "eating toast",
          "living the dream", "spying for the Russians", "cooking up a wicked lasagne", "hiding in a cupboard", "cowering in the basement"]
place = ["by the riverside", "in the sea", "round Johnny Vegas' house", "in a Wetherspoon's", "in Grimsbee", "up a mountain", 
          "six miles due west of Chester", "on a roundabout in Ipswich", "behind the bike sheds", "by the kettle", "under the rug", 
          "at monkey's favourite restaurant", "as near as you can usually get to Stonehenge"]
setting = ["by moonlight", "round the back", "covered in gravy", "but romantically lit", "by cover of darkness", "but really dimly lit",
            "under a pile of old rags", "never to be seen again", "where you thought it was in the first place", "where you left it"]
event = ["a storm in a tea cup", "magic", "drinking too much coffee", "the day of the week", "the moon and werewolves",
            "bad breath", "monkeys", "Johnny Vegas", "dehydration", "slightly inclement weather conditions", "the bad men", "delicious tea",
            "flash flooding", "a blown fuse on the kettle", "monkey's playing tennis"]
eventSuffix = ["causing it", "being the dominant factor", "being to blame", "being misunderstood", "and all that", ", and of course jazz",
                ", plus also the dark arts", "being at fault", "and possibly God", "but could just be chance", "and leaving the tea bag in too long"]
dueTo = ["due to", "because of", "caused by", "down to", "a consequence of", "despite", "made worse by", 
            "put down to", "taking in to account"]
reason = ["lack of salt", "under watering", "over watering", "reasons out of our control", "extenuating circumstances", "rust taking hold",
            "cattle in the road", "a damaged overhead power cable", "a monkey escaping from the zoo", "a lack of tea bags left in the cupboard",
            "monkey", "BBC Scotland", "Johnny Vegas", "bad timing", "using the finest dried tea leaves", "the wrong kind of leaves on the line",
            "drinking twelve cups of tea a day", "gout", "poor personal hygiene", "inferior tea bags"]
causing = ["causing", "resulting in", "leading to"]
outcome = ["death", "hair loss", "mass hysteria", "a brew going cold", "minor delays", "not much really",
            "the traffic being backed up for miles", "a minor cold", "a rip in the space-time continuum", "rain stopping play",
            "panic and blind chaos", "people to burst out in to song", "spontaneous joy"]
timePrefix = ["after", "on", "before", "around about, or perhaps circa on,", "almost definitely pre-"]
time = ["a week Wednesday", "Sunday evening", "Boxing day", "next never", "the stroke of midnight", "the next episode of Eastenders", 
        "Johnny Vegas' birthday", "a week next never", "every minute of every day of the rest of our lives"]
moment = ["having had 'that' chat", "monkey saying so", "making that brew", "adding the bag, then the water, then the milk, then the sugar"]
timeSuffix = ["straight after the One Show", "but only when the tea has properly brewed", "when the kettle boils",
              "if we haven't run out of tea bags", "if that isn't too much to ask", ", and having had another brew of course",
              "when we'll get a kebab and go to a disco", "or there or thereabouts"]
byTry = ["by", "try", "consider", "wikiHow says consider trying", "MumsNet suggests"]
method = ["rubbing a magic lamp", "adding white wine... or is it red wine", "counting backwards", "touching your nose with your elbow",
          "using Google", "reading all the endless online advice for days", "tossing a coin", "making a brew (which should always come first)",
          "switching it off and on again", "adding the bag, then the boiling water, then the milk, then the sugar", 
          "lifting up the bonnet and jet washing the swine", "hitting it with a hammer", "saying twelve Hail Marys"]
methodSuffix = ["and hoping for the best", "and praying", ", then having a quiet sit", "and adding an extra lump of sugar in your tea",
                "and just going for it", "and to hell with the consequences", "then gargling salt water", "and if that fails just quit",
                "and repeat if necessary", ", but do it in style", ", then rinse and repeat"]
about = ["about", "due to", "determined by", "a consequence of", "inherently down to"]
theProcess = ["the manner in which it was made", "the manufacturing process", "the build quality", "how it's put together", 
              "how you look at these things", "your perspective on life", "your star sign", "'math' and that", "cosmic ordering", 
              "chance", "your upbringing", "what it's actually made of", "the ingredients you use", "the choices you make", 
              "how the stars align", "the state of things these days", "your personal views"]
isIssue = ["is a problem for you", "scares you", "means it's all pointless anyway", "leads to the end of life as we know it", 
           "is your thing", "is a turn off", "is chronic", "is plausible"]

# Some random extra add-ons
randomExtras = {"is": ["just my luck!", "blooming typical!", "common these days", "par for the course", 
                        "nothing that can't be fixed with a nice cuppa", "sort of what you'd expect", "nothing to do with me"],
                "contradicts": ["what I just said", "the manual", "basic common sense", "the laws of physics"],
                "monkey thinks": ["is", ["the answer to everything", "inevitable", "best fixed with a nice cup of tea",
                                            "not that unusual in the current climate", "pretty standard"]],
                "honestly": [["beggars belief", "is not uncommon", "is astonishing", "is flabbergasting"],
                            [stop, skip], ["when", "if"], "you think about it"]}

caveats = [[",", stop], ["which is", skip], prefixAdverb+[skip], dueTo, event+reason, [skip, stop], "which", randomExtras]

whoList = [
            [["Who", "Whom"], ["do you think", "would you like it to be", "is anybody, really", "gives a damn", "goes there", 
                               "let The Dogs Out", "are you", "can live without it, I ask in all honesty", 
                               "lives in a house like this", "moved my cheese", "rattled your cage"], quiz],
            [prefix+[skip], itIs, prefixAdverb+[skip], identity, [skip, stop], doing+[skip, stop], 
                wearing+[stop], adjective+[skip], colour+[skip], clothes, [skip, stop], pairedWith+[skip, stop], whilstPrefix+[stop], whilst],
            [prefix, itIs, identity, doing],
            [identity]+caveats,
            ["It's not", identity, ["again", skip], "is it", quiz],
            [itIs+[skip], prefixAdverb, identity, wearing+[stop], adjective+[skip], colour+[skip], clothes],
            [prefixQuestion+[skip], itIs, prefixAdverb+[skip], identity, [skip, quiz], doing+[skip, quiz], wearing+[quiz],  
                adjective+[skip], colour+[skip], clothes, [skip, quiz], pairedWith+[skip, quiz], whilstPrefix+[quiz], whilst, quiz]
        ]

whatList = [
            ["What", ["do you think?", "is the point to be honest?", "is the meaning of this?", "on earth do you mean?",
                      "do you want from me? It's not how it used to be!", "time is dinner? I'm famished!",
                      "goes up must come down", "happens in Vegas, stays in Vegas!", "has come over you?", 
                      "have the Romans ever done for us?", "if...?", "in tarnation?", "in the name of Dickens!",
                      "is this life if, full of care, we have no time to stand and stare", "the Dickens!",
                      "do points mean? Points mean prizes!", "do you give to a man who has everything?", 
                      "does that have to do with the price of fish?", "fresh hell is this?", "gives?", "goes around comes around"]],
            [prefix+[skip], itIs, prefixAdverb+[skip], identity, [skip, stop], doing+[skip, stop], 
                wearing+[stop], adjective+[skip], colour+[skip], clothes, [skip, stop], pairedWith+[skip, stop], whilstPrefix+[stop], whilst],
            [prefix, itIs, identity, doing]+caveats,
            [identity]+caveats,
            [prefixAdverb, identity, wearing+[stop], adjective+[skip], colour+[skip], clothes],
            [prefixQuestion+[skip], itIs, prefixAdverb+[skip], identity, [skip, quiz], doing+[skip, quiz], 
                wearing+[quiz], adjective+[skip], colour+[skip], clothes, [skip, quiz], pairedWith+[skip, quiz], whilstPrefix+[quiz], whilst]
        ]

whereList = [
            ["Where", ["the sun meets the sky", "isn't it?", "have all the cowboys gone?", "the wild things are", 
                        "do you go, my lovely?", "do I even begin?", "am I!?!", "wonders never cease", "'s the catch?",
                        "did Our Love Go?", "eagles dare", "imagination meets reality", "it's at", "on god's green earth", 
                        {"would": [["you say it is", "you like it to be"], quiz]},
                        {"there's": ["smoke there's fire", "a will there's a way", "life, there's hope", "muck there's brass"]}]],
            [prefix+[skip], itIs, prefixAdverb+[skip], place, [skip, stop], setting+[skip, stop], dueTo, reason],
            [prefix, itIs, place, setting+[stop]]+caveats,
            [place]+caveats,
            [prefixQuestion+[skip], itIs, prefixAdverb+[skip], place, [skip, quiz], setting+[skip, quiz], quiz]+ 
                [["Because", "As"]+[skip], "that's" , ["where", "the kind of place"], 
                ["I'd", "monkey would", "Johnny Vegas would"], ["leave it", "put it"], stop]
        ]

whyList = [
            {"Why":{"":[["wouldn't it", "not", ", oh why, oh why...", "frankly who cares already",
                         "is it you get to ask all the questions", "do birds suddenly appear", "hast thou forsaken me", 
                         "does it always rain on me", "did the chicken cross the road", "do only fools and horses work",
                         "don't you say what you really think", "take two bottles into the shower"], quiz], 
                    "it's none of your business":[["you cheeky"]+[skip], ["monkey", "young scamp"],["!", stop]],
                    "you": ["!", "would, wouldn't you", "look lovely today", "might ask"]}},
            [prefix+[skip], itIs, prefixAdverb+[skip], dueTo, event, [skip, stop], eventSuffix],
            [prefix, itIs, dueTo, event, eventSuffix]+caveats,
            [prefix, itIs, dueTo, event]+caveats,
            [["Could it be"]+[skip], dueTo+[skip], reason, [skip, quiz], causing, outcome, quiz],
            [["Monkey thinks", "These days"]+[skip], itIs, prefixAdverb+[skip], dueTo, event, eventSuffix+[stop]],
            [prefixQuestion+[skip], itIs, prefixAdverb+[skip], event, [skip, quiz], place+[skip, quiz], quiz]+ 
                [["Because", "As"]+[skip], "that's" , ["why", "the reason"], ["I'd", "monkey would", "Johnny Vegas would"], 
                ["do it", "resort to that"], stop]
        ]

whenList = [
            {"": [["Monkey says", "When"], ["would you", "shall we three meet again", ", will I, will I be famous!", 
                   "is the best time for you"], quiz],
             "When": ["you're in love with a beautiful woman", "you're smiling, when you're smiling, the whole world smiles with you",
                      "push comes to shove", "it rains, it pours", "all is said and done", "in Rome...", "the going gets tough, the tough get going",
                      "hell freezes over", "I was a lad...", "I'm good and ready", "you least expect it", "the boat comes in", "word gets out",
                      "all is said and done", "all you have is a hammer, everything looks like a nail", "pigs fly", "the cat's away", 
                      "I was a kid, I walked to school uphill both ways", "the time is right", "you get a moment", "the going gets tough",
                      "the dust has settled", "the gloves are off", "the eagle flies", "the band begins to play", "the fat lady sings",
                      "the stars align"], 
             "Right after": ["you've made that brew!", "monkey's tidied his room", "you stick the kettle on", "we've had a quick brew"]},
            [prefix+[skip], itIs+[skip], prefixAdverb+[skip], timePrefix, time+moment, timeSuffix+[skip, stop]]+caveats,
            [itIs+[skip], timePrefix, moment, timeSuffix+[skip, stop]]+caveats,
            [timePrefix, time],
            [prefixQuestion+[skip], itIs+[skip], prefixAdverb+[skip], timePrefix, time+moment, timeSuffix+[skip, stop], quiz],
            [prefixQuestion+[skip], itIs+[skip], timePrefix, time, quiz]
        ]

howList = [
            ["How", ["do you do", "do you like your eggs in the morning", "would you like it", "you doing",
                     "is it you get to ask all the questions", "do you mean", "do they do that",
                      "long is a piece of string", "do you take your tea", "one lump or two", 
                      "soon is now", "deep Is Your Love", "about that", "come", "do you like them apples",
                      "does your garden grow", "long is a piece of string"], quiz],
            [["Monkey says", skip], "have you tried Googling it?", "how dare you!", "that's how, for now"],
            [prefix, prefixAdverb+[skip], byTry, method, methodSuffix+[skip]]+caveats,
            [prefix, byTry, method, methodSuffix+[skip]],
            [byTry, method],
            [prefixByTry, method, methodSuffix+[skip], [skip, quiz], whilstPrefix+[quiz], whilst],
            [prefixByTry, method, quiz]
        ]

decideList = [
            [["Yes", "No", "Affirmative", "No way!", "Is that even legal?", "Only if you ask nicely", 
                "Does a bear defecate in the woods?", "Is the Pope catholic?", "Do you really mean that?",
                "It's hard to say", "We could toss a coin to decide"]+prefixAdverb],
            ["That's", prefixAdverb, ["yes", "no", "not", "so", "the way it is", "the way the cookie crumbles", 
                            "how things will pan out", "the reasonable thing to assume"], ".", prefixByTry, method, quiz],
            [prefix+[skip], itIs, prefixAdverb, [", yes", "not", "implausible", "out of the question"]],
            [itIs, prefixAdverb+[skip], about, theProcess, ["as well as whether", "and also if"]+[stop], outcome+event, isIssue]+caveats,
            [itIs, about, theProcess, "and also", outcome]+caveats,
            [itIs, about, theProcess],
        ]

unsureList = [
            [["Monkey", "I"], ["really"]+[skip], ["shouldn't say", "don't care anymore", "don't understand"]],
            ["Monkey", ["don't know", "puzzled", "baffled"], ["about this", "why you ask"]+[skip]],
            [["I'm", "Monkey"], "speechless", ["for once!"]+[skip]],
            ["Monkey says", ["did you type something wrong?", "that's not something I can answer",
                            "it's all relative, really"]],
            [["Monkey says"]+[skip], "Good question", ["... or is it?"]+[skip]],
            [["Always with the questions damn you!", "Frankly, my dear, I don't give a damn",
                "Is the answer 42?", "Google's pretty good for that sort of thing",
                "That would be an ecumenical matter", "Generally, things are pretty futile these days"]],
            [["Janet", "Karen", "Barbara", "Deborah", "Daryl", "Keith"], "said on", ["Mumsnet", "Facebook", "X", "TikTok"],
                "that", ["Sheila", "Bryan", "Steve", "cheryl"], "said they'd heard",
                    ["the council were cutting back on that sort of thing",
                     "that was illegal now", "you shouldn't say that anymore",
                     "MySpace was all the rage right now", "it was going to happen anyway",
                     "planning permission had already been given, so..."]]
        ]

