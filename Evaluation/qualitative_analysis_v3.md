Gemini is good at recognizing specific letters and writing (eg. img. 1 it can recognize specific gravestones)

Gemini without gps is more consistantly confidently wrong (eg. image 1 description and location claims)

GCV disnt get the specific duomo in image 2 which is dissapointing

Very impressive that gpt vision direct strong got "Near Makartsteg footbridge, Salzburg" the exact bridge the photo was taken from without gps nor it being visible. A lot of models guessed a certain side of the river, but the photo was taken from the middle of a bridge. I will treat either side as correct. Image 4

Very impressive that Gemini vision strong got the exact street name right. image 5

For hard scenes with no visible landmarks, GPT without gps doesnt make location claims, just describes what it can see. Better than being wrong though, like gemini often does

Impressive that GCV got specific entities (a bit vague on "skyscraper" though). Image 6

GPT + search should look for signs or clues to search for and make location claims based on that. More potential here

GCV not really relevant or usable. Does not really add to anything. Good for recognizing text though

Weird that some models claim less specificity for parent claim. For example it claims "east side gallery" with higher confidence than "Fredrichein". Or "Fraternal kiss" higher than "grafitti". It does this several times. Ot "pyramids of giza" lower confidence than "Great pyramids of giza"

Weird that Gemini sometimes claims landmarks that are not visible in the photo, but close by. Maybe it makes guesses based on the google places input. Should be investigated.

For the future, mdoel should specify where in the photo it can see things

Should make it more clear to the models that the gps data indicates where the photo is from.

Gimini seems to be the clear winner of artwork. Look especially at image 29. It got the right painting, correctly described it and managed to get the connection between a shell with five balls to the medici coat of arms. 

Google maps places might throw it off because it gives FPs that are not in the image but close by. Better to use an MCP for this.

A lot of the mistakes were due to thinking landmarks are close by were visible in the frame. Maybe due to google places.

Somhow GCV sometimes gets it spot on. I cannot really see what the common denomiator is for this. IE image 56. 

Gemini needs to be told to be less confident, Ie. image 61 and 62. Should be told to generalize when unsure. It sometimes performs better without gps because doesnt hallucinate specifics. 

Chinese models were not tested because of censoring

Extremely impressed by both Gemini models without GPS on image 65. Maybe the photo resembles some google maps images? A definite strength for Gemini.

On image 71 without GPS, Gemini is far better

GPT fast is a very poor judge of distance, for example img 159 where the eiffel tower is far away, but it thinks the photographer is standing right next to it. Same wit surfers paradise in img 164