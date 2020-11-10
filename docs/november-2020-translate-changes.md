# November 2020 Google Translate API Changes

This analysis covers the analysis of the changes to Google Translate from around the beginning of November 2020. It'll be a work in progress until the time gTTS-token and the various upstream dependents have managed to work around the changes.

## Methodology

The first challenge is actually getting the updated Google Translate. In my experience using Firefox (not my default browser) in private mode gives me the new version *some* of the time. So if you want to follow along, trial and error is your friend. Also it'd make sense that the changes will be rolled out in certain regions before others, so you might just need to be more patient.

You can recognize the newer version by opening up your browser's dev tools, going to the network tab, typing some translation and hitting the speech button. The older version will trigger a call to `/translate_tts`, while the newer version will actually fetch the audio directly after you finished typing with a call to `/_/TranslateWebserverUi/data/batchexecute`. In fact you'll see many `batchexecute`s, it appears to be a generic endpoint for various RPCs.

Once you get this new version, keep it open to prevent having to go through the same hassle again. I've tried saving the page and hosting it myself, but hit various errors and CORS warnings. For now keeping the page open seems the best option. I'm open to suggestions.

## Network requests

Starting with what we know: we enter text, we press a button and we hear speech. That conversion must happen somewhere and indeed it's still done by making a request to a Google service. We can identify this firstly by comparing the response size of the `/translate_tts` with the `/batchexecute`. Testing with "Example" gives me a response size of 4.5KB on `/translate_tts` and I see 2 responses from `/batchexecute` one of 4.29KB and one of 5.76KB, these both have the parameter `rpcids` set to	"jQ1olc". To verify this, you can try longer texts and see that the the response size of these three calls will roughly match with any text.

Looking at the response, we see something like 
```javascript
)]}'

5564
[["wrb.fr","jQ1olc","[\"//NExAAR0NHwAVgQAGDpaGaB40eKGwSalDL993Xp7ff3hhhhhUpMNgAAT8hG99CAAAII7y+J1A+D4Ph/..."]\n",null,null,null,"generic"]
]
57
[["di",37]
,["af.httprm",36,"-668177807451224424",66]
]
27
[["e",4,null,null,5662]
]

```

The value starting with "//NExA" very much appears to be the audio encoded in base64. With the rest of the request being part of the RPC protocol. So we can be pretty sure the "jQ1olc" calls are correct.

Then why 2 and how do they differ? Well the request is mostly the same, except for the data passed. The first is
```
f.req	"[[[\"jQ1olc\",\"[\\\"Example\\\",\\\"en\\\",null,\\\"null\\\"]\",null,\"generic\"]]]"
```
and the second with the larger response is.
```
f.req	"[[[\"jQ1olc\",\"[\\\"Example\\\",\\\"en\\\",true,\\\"null\\\"]\",null,\"generic\"]]]"
```

The response isn't much different either, same structure, some different numbers and also different audio.

I've tried debugging the source of the network requests and didn't get much further, which let me to the next opening.

## Audio API

While all the code is obfuscated, we can be pretty sure Google is making audio somewhere. There are several ways. One is an `<audio>` element. To test this, I entered a pretty long text, had it read and fired `document.getElementsByTagName('audio')`. That yielded an empty collection on my machine. So we can be pretty sure, Google is using the JavaScript API (though I did find some code which could be a fallback to `<audio>` if the Javascript Web Audio API isn't available).

