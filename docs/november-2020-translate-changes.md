# November 2020 Google Translate API Changes

This analysis covers the analysis of the changes to Google Translate from around the beginning of November 2020. It'll be a work in progress until the time gTTS-token and the various upstream dependents have managed to work around the changes.

## Methodology

The first challenge is actually getting the updated Google Translate. In my experience using Firefox (not my default browser) in private mode gives me the new version *some* of the time. So if you want to follow along, trial and error is your friend. Also it'd make sense that the changes will be rolled out in certain regions before others, so you might just need to be more patient.

You can recognize the newer version by opening up your browser's dev tools, going to the network tab, typing some translation and hitting the speech button. The older version will trigger a call to `/translate_tts`, while the newer version will actually fetch the audio directly after you finished typing with a call to `/_/TranslateWebserverUi/data/batchexecute`. In fact you'll see many `batchexecute`s, it appears to be a generic endpoint for various RPCs.

Once you get this new version, keep it open to prevent having to go through the same hassle again. I've tried saving the page and hosting it myself, but hit various errors and CORS warnings. For now keeping the page open seems the best option. I'm open to suggestions.

## Network requests

Starting with what we know: we enter text, we press a button and we hear speech. That conversion must happen somewhere and indeed it's still done by making a request to a Google service. We can identify this firstly by comparing the response size of the `/translate_tts` with the `/batchexecute`. Testing with "Example" gives me a response size of 4.5KB on `/translate_tts` and I see 2 responses from `/batchexecute` one of 4.29KB and one of 5.76KB, these both have the parameter `rpcids` set to	"jQ1olc". As an aside: one prominent change in the new version is that the audio is fetched when you hover over the speech button, which is a pretty cool optimization, making the user wait just a tiny bit shorter. To verify these requests are actually the suspects, you can try longer texts and see that the the response size of these three calls will roughly match with any text.

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

So while the code itself might be obfuscated, the interfacing with the Web Audio API must use those proper names. Thus we embark on a new journey.

Switching to the Debugger or Sources tab in your dev tools, you can search through all the code with `ctrl + shift + f` or `cmd + shift + f`. Searching for "Audio" yields several results with 18 of those being in [_/mss/boq-translate/_/js/k=boq-translate.TranslateWebserverUi.nl.v8w1lBlfuAo.es5.O](https://www.gstatic.com/_/mss/boq-translate/_/js/k=boq-translate.TranslateWebserverUi.nl.v8w1lBlfuAo.es5.O/ck=boq-translate.TranslateWebserverUi.TNhbPT4jnLs.L.F4.O/am=gAI/d=1/exm=A7fCU,AKLKy,AV6dJd,BVgquf,CBlRxf,COQbmf,EFQ78c,G0j0Je,GSlykd,GiFjve,HDvRde,HLo3Ef,I6YDgd,IZT63,Id96Vc,Izs65d,JE2clc,JNoxi,K4PcAe,KG2eXe,KOuY1b,KUM7Z,L1AAkb,LEikZe,MDB2J,MnwvSb,MpJwZc,N2mfec,NotTJb,NpD4ec,NufREb,NwH0H,O6y8ed,OmgaI,PJgxJf,PQaYAf,PrPYRd,QIhFr,Qnj3Pe,RMhBfe,Ru0Pgb,SF3gsd,SNtCZb,SdcwHb,SpsfSb,TzmfU,U0aPgd,UUJqVe,UWMmZb,Uas9Hd,UgAtXe,Ulmmrd,UthHZe,V3dDOb,VETAO,VwDzFe,WO9ee,XBRlNc,XVMNvd,Y2UGcc,YLQSd,YrN4Fb,ZfAoz,ZwDk9d,_b,_tp,aW3pY,aurFic,bD99Db,bYHiff,blwjVc,byfTOb,duFQFc,ehH0Pd,fKUV3e,g8fAWe,gWGePc,glibvb,gychg,hB8iWe,hc6Ubd,iTsyac,iWP1Yb,jl0Zdc,lPKSwe,lsjVmc,lwddkf,mNvcvf,mmcjze,n391td,n73qwf,o02Jie,p8L0ob,pB6Zqd,pjICDe,pw70Gc,rE6Mgd,rHjpXd,rPRh8e,s2VbJb,s39S4,tfTN8c,tjiVBd,w9hDv,wLUyde,ws9Tlc,x60fie,xQtZb,xUdipf,xiqEse,yDVVkb,zbML3c/excm=_b,_tp,mainview/ed=1/wt=2/ct=zgms/rs=ANkVxDma2FRJ_-xLX9vGpJ6HkRmLaNVkRQ/m=GILUZe,i5dxUd,RAnnUd,UECOXe,eYJrS,sJhETb,JH2zc,qAKInc,fR6Vdb,IjTJJb,uu7UOe,t1sulf,soHxf,xzbRj,VNcg1e,Xn16n,hPAkKe,fmklff,s2XCRc,ZbunN,WYNSOe,hmxKAd,P6Sgne,MY2OBe,MaBk4,MJWMce,Y9atKf,JWUKXe,pPThOe,xdp6Ne,tQX3bd,HwavCb,ff8rzd,ryfyqf,gJzDyc,onWwzb,CW8lw,UfGXTd,LP4cEc,Un38xf,ZH8ved,QKK0O,AJZZxc,fKBXPe,WCciof,JPvYpc,sGhhBd,JNcm2e,TJQ3Ud,JVNQkc,cPVRG,M2suMc). I would expect at least the `nl` part of that URI to differ for most readers. Once we open that file, I highly recommend enabling pretty print. With that we can continue our search for "audio" with `ctrl + f` or `cmd + f` and we'll find the following snippet.

```javascript
    KOa = function (a, b) {
      return new Promise(function (c, d) {
        Uint8Array.from || (console.warn('Attempting to decode audio when TTS is unsupported'), c((new Uint8Array(0)).buffer));
        a.decodeAudioData(Uint8Array.from(atob(b), function (e) {
          return e.toString().charCodeAt(0)
        }).buffer, c, d)
      })
    };
```

This is taking a base64 string `b`, base64 decoding it (`atob`), turning it into a Uint8Array (`Uint8Array.from`) based on the charcode of each character (`e.toString().charCodeAt(0)`) and then decoding that audio `a.decodeAudioData`. Small aside, the `toString()` appears to be superfluous here, maybe Google is using TypeScript(?). If we set a breakpoint and change the text in your translate field, we'll see that the value of `b` is the same as the value following "jQ1olc" from the first request (the one with `null` instead of `true`).

To double check things, we'll try to use the response to create our own audio.

```javascript
const response = ...; // Paste the response from the [['wrb.fr' to the final ]
const encodedAudio = eval(response[0][2])[0] // Be sure to check the value of response so you don't `eval` anything dangerous
const decoded = Uint8Array.from(atob(encodedAudio), (e) => e.charCodeAt(0));
const context = new AudioContext();
const source = context.createBufferSource();
context.decodeAudioData(decoded.buffer, (audioBuffer) => { source.buffer = audioBuffer; source.connect(context.destination); source.start(0); })
```

You should hear the text you entered. With all this confirmed, now all we have to do is find a way to call "jQ1olc" ourselves. More to follow.

## Ladies and gentlemen, we've got him

[I think I have a mostly working implementation](https://github.com/Boudewijn26/gTTS/commit/aea95c9623985c02a95483d49ebec6dae61b956c). I'll walk you through how I got there.

Taking the request to "jQ1olc", the first thing one should try is just replaying it. Most dev tools will allow you to do so with right clicking on the request in your network tab. This succeeds and tells us there is no single use token. Waiting an hour and replaying and we can be sure there is no time based token at work either. Then it's time to play around with the request. My favorite tool for this is Postman. You can copy the request to cURL and import it into Postman without a hassle. There are many other tools, which do the same, I'm familiar with Postman.

Once there, the first thing to try is changing the text while keeping everything the same. That'll tell if there is a special value being calculated based on the text itself, which we'd have to recreate. This still succeeds. Looking good. Only thing left is to see which of all these values are actually necessary. So if we flip them off one by one, after a while we're left with:

* The Content-Type header
* None of the query params
* The POST body

Then how is the body constructed? The raw body looks something like

```
f.req=%5B%5B%5B%22jQ1olc%22%2C%22%5B%5C%22hello%5C%22%2C%5C%22en%5C%22%2Cnull%2C%5C%22null%5C%22%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&
```

That certainly looks uri encoded and indeed:

```javascript
decodeURIComponent("%5B%5B%5B%22jQ1olc%22%2C%22%5B%5C%22hello%5C%22%2C%5C%22en%5C%22%2Cnull%2C%5C%22null%5C%22%5D%22%2Cnull%2C%22generic%22%5D%5D%5D")
=> "[[["jQ1olc","[\"hello\",\"en\",null,\"null\"]",null,"generic"]]]"
```

So, 3 arrays nested inside each other. The inner array has `"jQ1olc"`, `"[\"hello\",\"en\",null,\"null\"]"`, `null`, `"generic"`. As elements. As indicated by the rpcids param, the `"jQ1olc"` is the name of the RPC we're calling. `"[\"hello\",\"en\",null,\"null\"]"` appears to be another array which was `JSON.stringify`d. Not sure what `null` is doing, we see it in all of the other RPCs as well. `"generic"` appears to be indicate the type of RPC.

So on to splitting out `"[\"hello\",\"en\",null,\"null\"]"`. As stated this is another array which is `JSON.stringify`d. We have `"hello"` which is our text. `"en"` which is our locale. Spoiling a bit of the results `null` or `true` in the second request appears to be the speed, with `true` being slower, which is why that response is a bit bigger. The difference doesn't seem to be very big, but still noticable. I've yet to find out what `"null"` is doing, it could perhaps indicate the preferred voice style. Why this is a `"null"` string instead of `null` is also unclear to me.

So if you want to build this payload, we build an array of our text, locale, `null` or `true` and "null". `JSON.stringify` it. Build a nesting of 3 arrays with the inner one being "jQ1olc", the result of `stringify`, `null` and "generic". Then `encodeURIComponent` it. Or in code

```javascript
function(text, locale, slow) {
  return encodeURIComponent([[["jQ1olc", JSON.stringify([text, locale, slow ? true : null, "null"]), null, "generic"]]]);
}
```

You can try some texts, copy the result from Postman and throw it into our audio decode snippet from above to verify. In all this, you may notice a distinct lack of tokens in there. This isn't looking very good for gTTS-token. Oh well.

## Finishing up

So all that's left is to port this to Python. I've already gotten a [working version of gTTS](https://github.com/Boudewijn26/gTTS), so it's looking very promising. Just some finishing up to finalize it.

However this does appear to leave gTTS-token in a bit of a void. A project specifically written to generate tokens for a service which no longer requires tokens, isn't particularly useful. I'll update the README to reflect that aspect of this project and let this guide serve as a means for everyone to update their implementations and help with future investigations. Feel free to @ me if/when things break again.
