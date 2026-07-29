"""Servidor local para una neurona visual enseñable, sin dependencias externas."""

from __future__ import annotations

import json
import math
import random
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse


SAMPLES: list[dict] = []
MODEL: dict | None = None

APP_HTML = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NeuronaLab</title>
<style>
:root{--bg:#050c0a;--panel:#0a1712;--line:#19352b;--lime:#baff29;--cyan:#2fffd2;--text:#effff8;--muted:#78968b}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 10% 0,#164432,transparent 35rem),var(--bg);color:var(--text);font-family:system-ui,sans-serif;min-height:100vh}
body:before{content:"";position:fixed;inset:0;pointer-events:none;opacity:.2;background-image:linear-gradient(#183329 1px,transparent 1px),linear-gradient(90deg,#183329 1px,transparent 1px);background-size:42px 42px}
main{position:relative;width:min(1450px,95vw);margin:auto}nav{height:62px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between}.brand{font-weight:900;letter-spacing:.12em}.brand b{color:var(--lime)}.modeNav{display:flex;gap:5px;background:#07110e;border:1px solid var(--line);padding:4px;border-radius:8px}.modeNav button{padding:7px 13px;background:transparent;color:var(--muted);font-size:.7rem}.modeNav button.active{background:var(--lime);color:#06110d}.modeNav button:disabled{opacity:.3}
.status{font-size:.72rem;border:1px solid var(--line);border-radius:99px;padding:8px 13px;color:#a9c0b7}.status i{display:inline-block;width:8px;height:8px;background:var(--lime);border-radius:50%;box-shadow:0 0 12px var(--lime);margin-right:8px}
header{display:flex;align-items:end;justify-content:space-between;padding:42px 0 28px}.eyebrow{color:var(--cyan);font-size:.7rem;font-weight:800;letter-spacing:.15em}h1{font:800 clamp(3rem,7vw,6.5rem)/.86 Georgia,serif;letter-spacing:-.06em;margin:10px 0}h1 em{color:var(--lime)}header p{color:#9bb0a8;max-width:650px}.stats{display:flex;border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#08120f}.stats div{text-align:center;padding:12px 20px;border-left:1px solid var(--line);min-width:95px}.stats div:first-child{border:0}.stats strong,.stats small{display:block}.stats strong{color:var(--lime);font:700 1.3rem monospace}.stats small{font-size:.58rem;color:var(--muted);letter-spacing:.1em}
.grid{display:grid;grid-template-columns:1.1fr .9fr 1fr;gap:14px}.card{background:linear-gradient(145deg,#0d1b16f2,#07110ef2);border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 18px 55px #0005}.title{font-size:.68rem;font-weight:900;letter-spacing:.14em;margin-bottom:14px}.title b{color:var(--lime);border:1px solid #426453;border-radius:4px;padding:4px 6px;margin-right:8px}.title em{float:right;color:#39b98b;font-style:normal;font-size:.55rem}
.camera{aspect-ratio:4/3;position:relative;background:#020705;border:1px solid var(--line);border-radius:9px;overflow:hidden}.camera video{width:100%;height:100%;object-fit:cover;transform:scaleX(-1)}.placeholder{position:absolute;inset:0;display:grid;place-items:center;color:#61766e}.scan{display:none;position:absolute;left:0;width:100%;height:1px;background:var(--lime);box-shadow:0 0 10px var(--lime);animation:scan 2.4s infinite}@keyframes scan{0%,100%{top:8%}50%{top:92%}}
.result{display:none;position:absolute;left:12px;bottom:12px;background:#06110dec;border-left:3px solid var(--lime);padding:9px 12px}.result small,.result span{display:block;color:var(--muted);font-size:.62rem}.result strong{display:block;color:var(--lime);font:700 1.45rem Georgia,serif}
button,input{font:inherit}button{border:0;border-radius:7px;padding:11px 15px;background:var(--lime);color:#06110d;font-weight:850;cursor:pointer}button:hover{box-shadow:0 0 20px #baff2940}button:disabled{opacity:.35;cursor:not-allowed;box-shadow:none}.cameraBtn{width:100%;margin-top:9px;background:#103326;color:var(--cyan);border:1px solid #245a45}.ghost{background:transparent;color:var(--muted);border:1px solid var(--line)}
label{display:block;font:700 1rem Georgia,serif;margin:22px 0 7px}.row{display:flex;gap:7px}input{width:100%;min-width:0;background:#030806;color:var(--text);border:1px solid var(--line);border-radius:7px;padding:11px;outline:0}input:focus{border-color:var(--cyan)}.help{color:var(--muted);font-size:.74rem;line-height:1.5}.classes{height:135px;overflow:auto;margin:10px 0}.class{display:flex;justify-content:space-between;border-bottom:1px solid var(--line);padding:8px 2px;font-size:.78rem}.class b{color:var(--cyan)}.actions{display:flex;gap:7px}.notice{border:1px solid #685b24;background:#1e1a0b;color:#e8d979;border-radius:7px;padding:9px;font-size:.7rem;margin:10px 0}.testGuide{display:none;margin-top:10px;border:1px solid #287c5d;background:#0b2b20;color:#a9f6d7;border-radius:7px;padding:10px;font-size:.72rem;line-height:1.45}.testGuide b{display:block;color:var(--lime);margin-bottom:3px}
canvas{display:block;width:100%}.brain{height:225px}.graph{height:330px;background:radial-gradient(circle,#10291f,#030806 70%);border:1px solid var(--line);border-radius:8px}.wide{grid-column:1/3}.lossCard{grid-column:3}.loss{height:330px;background:#030806;border:1px solid var(--line);border-radius:8px}.bars{border-top:1px solid var(--line);padding-top:8px;min-height:74px}.bar{font-size:.67rem;margin:7px 0}.barHead{display:flex;justify-content:space-between}.track{height:4px;background:#15251f}.fill{height:100%;background:linear-gradient(90deg,#24a978,var(--lime))}
body[data-mode="test"] #teachCard,body[data-mode="test"] #graphCard,body[data-mode="test"] #lossCard{display:none}body[data-mode="test"] .grid{grid-template-columns:1.25fr 1fr;max-width:1050px;margin:auto}body[data-mode="test"] #cameraCard,body[data-mode="test"] #brainCard{min-height:520px}body[data-mode="test"] .result{display:block}footer{display:flex;justify-content:space-between;padding:18px 2px;color:var(--muted);font-size:.68rem}footer b{color:var(--cyan)}@media(max-width:900px){header{display:block}.stats{margin-top:20px}.grid,body[data-mode="test"] .grid{grid-template-columns:1fr 1fr}.wide,.lossCard{grid-column:1/-1}}@media(max-width:600px){nav{height:auto;padding:10px 0;gap:8px;flex-wrap:wrap}.grid,body[data-mode="test"] .grid{grid-template-columns:1fr}.wide,.lossCard{grid-column:auto}.row{flex-direction:column}header{padding-top:25px}}
</style>
</head>
<body data-mode="train"><main>
<nav><div class="brand">◆ NEURONA<b>LAB</b></div><div class="modeNav"><button class="active" id="trainModeBtn">1 · ENTRENAR</button><button id="testModeBtn" disabled>2 · PROBAR IA</button></div><div class="status"><i></i><span id="status">Servidor conectado</span></div></nav>
<header><div><div class="eyebrow">INTELIGENCIA VISUAL · ENTRENAMIENTO LOCAL</div><h1>Enséñale a <em>mirar.</em></h1><p>Muéstrale objetos, guarda recuerdos y observa cómo se conectan dentro de la red.</p></div><div class="stats"><div><strong id="samples">0</strong><small>MEMORIAS</small></div><div><strong id="concepts">0</strong><small>CONCEPTOS</small></div><div><strong id="state">OFF</strong><small>MODELO</small></div></div></header>
<section class="grid">
<article class="card" id="cameraCard"><div class="title"><b>01</b>ENTRADA VISUAL <em>LIVE</em></div><div class="camera"><video id="video" autoplay playsinline muted></video><canvas id="capture" width="16" height="16" hidden></canvas><div class="placeholder" id="placeholder">Conecta la cámara para comenzar</div><div class="scan" id="scan"></div><div class="result" id="result"><small>LA IA VE</small><strong>—</strong><span>sin predicción</span></div></div><button class="cameraBtn" id="cameraBtn">● Conectar cámara</button></article>
<article class="card" id="teachCard"><div class="title"><b>02</b>CREAR MEMORIA</div><label for="label">¿Qué estás mostrando?</label><div class="row"><input id="label" maxlength="40" placeholder="lápiz, celular, taza…"><button id="captureBtn">Capturar</button></div><p class="help">Guarda entre 10 y 20 capturas mientras mueves ligeramente el objeto. Enseña también una clase llamada <b>fondo</b>, sin ningún objeto, para detectar cuándo no reconoce algo.</p><div class="notice" id="notice">Necesitas enseñar al menos 2 objetos diferentes antes de entrenar.</div><div class="classes" id="classes"><p class="help">Aún no hay recuerdos.</p></div><div class="actions"><button id="trainBtn">⚡ Entrenar</button><button class="ghost" id="resetBtn">Reiniciar</button></div><div class="testGuide" id="testGuide"><b>✓ ENTRENAMIENTO TERMINADO</b>El modelo está listo. Pulsa «2 · PROBAR IA» en la parte superior.</div></article>
<article class="card" id="brainCard"><div class="title"><b>03</b>RED NEURONAL <em id="brainState">EN ESPERA</em></div><canvas class="brain" id="brain"></canvas><div class="bars" id="bars"><p class="help">Entrena para activar las conexiones.</p></div></article>
<article class="card wide" id="graphCard"><div class="title"><b>04</b>GRAFO DE RECUERDOS <em>CADA NODO ES UNA CAPTURA</em></div><canvas class="graph" id="graph"></canvas></article>
<article class="card lossCard" id="lossCard"><div class="title"><b>05</b>APRENDIZAJE <em>ERROR ↓</em></div><canvas class="loss" id="loss"></canvas><p class="help" id="lossText">Esperando entrenamiento…</p></article>
</section><footer><b>PRIVACIDAD LOCAL</b><span>La cámara y el aprendizaje permanecen en tu computadora.</span></footer>
</main>
<script>
const $=s=>document.querySelector(s),video=$("#video"),cap=$("#capture"),cx=cap.getContext("2d",{willReadFrequently:true});
let stream=null,trained=false,predicting=false,points=[],labels=[],losses=[];const colors=["#baff29","#2fffd2","#ffcc45","#ff6b9d","#a98bff","#42a5ff"];
function status(t){$("#status").textContent=t}function color(l){return colors[Math.max(0,[...new Set(points.map(p=>p.label))].indexOf(l))%colors.length]}
async function api(path,data={}){try{const r=await fetch(path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)}),j=await r.json();if(!r.ok)throw Error(j.error);return j}catch(e){throw Error("No se pudo conectar con Python. Ejecuta python app.py y usa http://127.0.0.1:8000")}}
function features(){cx.save();cx.translate(16,0);cx.scale(-1,1);cx.drawImage(video,0,0,16,16);cx.restore();const p=cx.getImageData(0,0,16,16).data,o=[];for(let y=2;y<14;y++)for(let x=2;x<14;x++){let i=(y*16+x)*4;o.push(p[i]/255,p[i+1]/255,p[i+2]/255)}return o}
function setMode(mode){if(mode==="test"&&!trained)return;document.body.dataset.mode=mode;$("#trainModeBtn").classList.toggle("active",mode==="train");$("#testModeBtn").classList.toggle("active",mode==="test");status(mode==="test"?"MODO PRUEBA · Muestra un objeto":"MODO ENTRENAMIENTO")}
$("#trainModeBtn").onclick=()=>setMode("train");$("#testModeBtn").onclick=()=>setMode("test");
$("#cameraBtn").onclick=async()=>{try{stream=await navigator.mediaDevices.getUserMedia({video:{width:640,height:480,facingMode:"user"},audio:false});video.srcObject=stream;$("#placeholder").style.display="none";$("#scan").style.display="block";$("#cameraBtn").disabled=true;$("#cameraBtn").textContent="Cámara conectada";status("Cámara activa");if(trained&&!predicting)loop()}catch(e){status("Cámara bloqueada");alert("Permite el acceso a la cámara en el navegador.")}};
async function refresh(){const r=await fetch("/api/status").then(x=>x.json()),entries=Object.entries(r.counts);if(r.trained){trained=true;labels=r.labels||labels}$("#samples").textContent=entries.reduce((s,x)=>s+x[1],0);$("#concepts").textContent=entries.length;$("#state").textContent=r.trained?"ON":"OFF";$("#testModeBtn").disabled=!r.trained;$("#trainBtn").disabled=entries.length<2;$("#notice").style.display=entries.length<2?"block":"none";$("#classes").innerHTML=entries.length?entries.map(([n,c])=>`<div class="class"><span>${safe(n)}</span><b>${c} recuerdos</b></div>`).join(""):'<p class="help">Aún no hay recuerdos.</p>'}
function safe(v){const d=document.createElement("div");d.textContent=v;return d.innerHTML}
function phrase(label){if(label==="fondo")return"No veo un objeto conocido";const feminine=/a$/.test(label.toLowerCase());return`Es ${feminine?"una":"un"} ${label}`}
$("#captureBtn").onclick=async()=>{if(!stream)return alert("Primero conecta la cámara.");if(video.readyState<2)return alert("Espera un momento: la cámara todavía está iniciando.");const label=$("#label").value.trim();if(!label)return alert("Escribe el nombre del objeto.");const f=features();try{await api("/api/sample",{label,features:f});points.push({label});trained=false;predicting=false;$("#state").textContent="OFF";status(`Memoria guardada: ${label}`);await refresh()}catch(e){alert(e.message)}};
$("#trainBtn").onclick=async()=>{status("Entrenando conexiones…");$("#trainBtn").disabled=true;try{const r=await api("/api/train");labels=r.labels;losses=r.history;trained=true;$("#state").textContent="ON";$("#brainState").textContent="ACTIVA";$("#testGuide").style.display="block";drawLoss();status(`ENTRENAMIENTO TERMINADO · ${r.samples} recuerdos`);if(!predicting)loop()}catch(e){alert(e.message);status("Faltan conceptos")}await refresh()};
$("#resetBtn").onclick=async()=>{if(!confirm("¿Borrar todos los recuerdos?"))return;await api("/api/reset");points=[];labels=[];losses=[];trained=false;predicting=false;setMode("train");$("#result").style.display="none";$("#testGuide").style.display="none";$("#bars").innerHTML='<p class="help">Entrena para activar las conexiones.</p>';$("#brainState").textContent="EN ESPERA";drawLoss();refresh();status("Memoria borrada")};
async function loop(){predicting=true;let spoken="",stable=0;while(trained){if(stream&&video.readyState>=2)try{const r=await api("/api/predict",{features:features()}),sure=r.confidence>=.6,name=sure?phrase(r.label):"No estoy segura";$("#result").style.display="block";$("#result strong").textContent=name;$("#result span").textContent=Math.round(r.confidence*100)+"% de seguridad";$("#bars").innerHTML=r.probabilities.map(x=>`<div class="bar"><div class="barHead"><span>${safe(x.label)}</span><b>${Math.round(x.value*100)}%</b></div><div class="track"><div class="fill" style="width:${x.value*100}%"></div></div></div>`).join("");if(spoken===name)stable++;else{spoken=name;stable=0}if(sure&&stable===3&&r.confidence>.72){speechSynthesis.cancel();const voice=new SpeechSynthesisUtterance(name);voice.lang="es-ES";speechSynthesis.speak(voice)}}catch(e){trained=false}await new Promise(r=>setTimeout(r,650))}predicting=false}
function fit(c){let d=devicePixelRatio||1,b=c.getBoundingClientRect();if(c.width!==b.width*d||c.height!==b.height*d){c.width=b.width*d;c.height=b.height*d}let x=c.getContext("2d");x.setTransform(d,0,0,d,0,0);return{x,w:b.width,h:b.height}}
function graph(t){const{x,w,h}=fit($("#graph"));x.clearRect(0,0,w,h);let cx=w/2,cy=h/2,ls=[...new Set(points.map(p=>p.label))],orbit=Math.min(w*.31,h*.33);x.strokeStyle="#17382d";[55,orbit].forEach(r=>{x.beginPath();x.arc(cx,cy,r,0,7);x.stroke()});ls.forEach((l,i)=>{let a=-Math.PI/2+i/ls.length*Math.PI*2,nx=cx+Math.cos(a)*orbit,ny=cy+Math.sin(a)*orbit,c=color(l);x.setLineDash([4,5]);x.strokeStyle=c;x.globalAlpha=.35;x.beginPath();x.moveTo(cx,cy);x.lineTo(nx,ny);x.stroke();x.setLineDash([]);let q=(t/1500+i/ls.length)%1;x.globalAlpha=1;x.fillStyle=c;x.beginPath();x.arc(cx+(nx-cx)*q,cy+(ny-cy)*q,3,0,7);x.fill();let mem=points.filter(p=>p.label===l);mem.forEach((p,j)=>{let s=(j-(mem.length-1)/2)*.22,d=34+(j%3)*10,mx=nx+Math.cos(a+s)*d,my=ny+Math.sin(a+s)*d;x.globalAlpha=.2;x.beginPath();x.moveTo(nx,ny);x.lineTo(mx,my);x.stroke();x.globalAlpha=.8;x.beginPath();x.arc(mx,my,2.5,0,7);x.fill()});x.globalAlpha=1;x.fillStyle="#08140f";x.strokeStyle=c;x.lineWidth=2;x.beginPath();x.arc(nx,ny,10,0,7);x.fill();x.stroke();x.fillStyle="#effff8";x.font="600 11px system-ui";x.textAlign="center";x.fillText(l,nx,ny+25)});let r=18+Math.sin(t/300)*2;x.fillStyle="#baff29";x.shadowColor="#baff29";x.shadowBlur=24;x.beginPath();x.arc(cx,cy,r,0,7);x.fill();x.shadowBlur=0;x.fillStyle="#06110d";x.font="900 9px monospace";x.textAlign="center";x.fillText("IA",cx,cy+3);requestAnimationFrame(graph)}
function brain(t){const{x,w,h}=fit($("#brain"));x.clearRect(0,0,w,h);let count=Math.max(2,labels.length),cols=[6,8,6,count].map((n,k)=>Array.from({length:n},(_,i)=>({x:22+k*(w-44)/3,y:h*(i+1)/(n+1)})));for(let k=0;k<3;k++)for(const a of cols[k])for(const b of cols[k+1]){x.globalAlpha=labels.length&&Math.floor(t/400+a.y+b.y)%7===0?.7:.16;x.strokeStyle=labels.length?"#baff29":"#285142";x.beginPath();x.moveTo(a.x,a.y);x.lineTo(b.x,b.y);x.stroke()}x.globalAlpha=1;cols.forEach((c,k)=>c.forEach(n=>{x.fillStyle=k===3?"#baff29":k===0?"#2fffd2":"#31745d";x.beginPath();x.arc(n.x,n.y,k===3?5:3.5,0,7);x.fill()}));requestAnimationFrame(brain)}
function drawLoss(){const{x,w,h}=fit($("#loss"));x.clearRect(0,0,w,h);x.strokeStyle="#17382d";for(let y=30;y<h;y+=45){x.beginPath();x.moveTo(0,y);x.lineTo(w,y);x.stroke()}if(!losses.length){$("#lossText").textContent="Esperando entrenamiento…";return}let max=Math.max(...losses),p=22;x.strokeStyle="#baff29";x.lineWidth=2;x.beginPath();losses.forEach((v,i)=>{let px=p+i/(losses.length-1)*(w-p*2),py=p+v/max*(h-p*2);i?x.lineTo(px,py):x.moveTo(px,py)});x.stroke();$("#lossText").textContent=`Error ${losses[0]} → ${losses.at(-1)}`}
refresh();drawLoss();requestAnimationFrame(graph);requestAnimationFrame(brain);addEventListener("resize",drawLoss);
</script></body></html>"""


def softmax(values: list[float]) -> list[float]:
    peak = max(values)
    exps = [math.exp(value - peak) for value in values]
    total = sum(exps)
    return [value / total for value in exps]


def train_network(epochs: int = 180, learning_rate: float = 0.12) -> dict:
    global MODEL
    labels = sorted({sample["label"] for sample in SAMPLES})
    if len(labels) < 2:
        raise ValueError("Enseña al menos dos clases diferentes.")

    size = len(SAMPLES[0]["features"])
    rng = random.Random(42)
    weights = [[rng.uniform(-0.03, 0.03) for _ in range(size)] for _ in labels]
    biases = [0.0 for _ in labels]
    label_index = {label: index for index, label in enumerate(labels)}
    history: list[float] = []

    for epoch in range(epochs):
        shuffled = SAMPLES[:]
        rng.shuffle(shuffled)
        loss = 0.0
        for sample in shuffled:
            x = sample["features"]
            target = label_index[sample["label"]]
            scores = [
                sum(weight * value for weight, value in zip(row, x)) + biases[i]
                for i, row in enumerate(weights)
            ]
            probabilities = softmax(scores)
            loss -= math.log(max(probabilities[target], 1e-9))

            for output in range(len(labels)):
                error = probabilities[output] - (1.0 if output == target else 0.0)
                for feature in range(size):
                    weights[output][feature] -= learning_rate * error * x[feature]
                biases[output] -= learning_rate * error

        if epoch % 10 == 0 or epoch == epochs - 1:
            history.append(round(loss / len(SAMPLES), 4))

    MODEL = {"labels": labels, "weights": weights, "biases": biases}
    return {"labels": labels, "history": history, "samples": len(SAMPLES)}


def predict(features: list[float]) -> dict:
    if not MODEL:
        raise ValueError("Primero debes entrenar la neurona.")
    if len(features) != len(MODEL["weights"][0]):
        raise ValueError("La imagen tiene un tamaño de características incorrecto.")

    scores = [
        sum(weight * value for weight, value in zip(row, features)) + MODEL["biases"][i]
        for i, row in enumerate(MODEL["weights"])
    ]
    probabilities = softmax(scores)
    ranking = sorted(
        zip(MODEL["labels"], probabilities), key=lambda item: item[1], reverse=True
    )
    return {
        "label": ranking[0][0],
        "confidence": round(ranking[0][1], 4),
        "probabilities": [
            {"label": label, "value": round(value, 4)} for label, value in ranking
        ],
    }


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/status":
            counts: dict[str, int] = {}
            for sample in SAMPLES:
                counts[sample["label"]] = counts.get(sample["label"], 0) + 1
            self.send_json(
                200,
                {
                    "counts": counts,
                    "trained": MODEL is not None,
                    "labels": MODEL["labels"] if MODEL else [],
                },
            )
            return
        if path in ("/", "/index.html"):
            body = APP_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404, "Ruta no encontrada")

    def do_POST(self) -> None:
        global MODEL
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            path = urlparse(self.path).path

            if path == "/api/sample":
                label = str(data.get("label", "")).strip()[:40]
                features = data.get("features")
                if not label or not isinstance(features, list) or not features:
                    raise ValueError("Falta la etiqueta o la imagen.")
                SAMPLES.append(
                    {"label": label, "features": [float(value) for value in features]}
                )
                MODEL = None
                self.send_json(200, {"ok": True, "total": len(SAMPLES)})
            elif path == "/api/train":
                self.send_json(200, train_network())
            elif path == "/api/predict":
                self.send_json(200, predict([float(v) for v in data["features"]]))
            elif path == "/api/reset":
                SAMPLES.clear()
                MODEL = None
                self.send_json(200, {"ok": True})
            else:
                self.send_json(404, {"error": "Ruta no encontrada."})
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})


if __name__ == "__main__":
    address = ("127.0.0.1", 8000)
    url = "http://127.0.0.1:8000"
    print(f"NeuronaLab disponible en {url}")
    print("Abriendo el navegador. Presiona Ctrl+C para detenerla.")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        ThreadingHTTPServer(address, Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nNeuronaLab detenido.")
