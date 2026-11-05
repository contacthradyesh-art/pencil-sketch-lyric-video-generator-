#!/usr/bin/env python3
"""Forced-align supplied lyrics. Missing words are never assigned guessed timestamps."""
import argparse,json,re,sys
from pathlib import Path
try:\n    from src.validators import validate_word_timings\nexcept ModuleNotFoundError:\n    from validators import validate_word_timings
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument("--audio",type=Path,default=ROOT/"temp/vocals.wav");p.add_argument("--lyrics",type=Path,default=ROOT/"input/lyrics.txt");p.add_argument("--output",type=Path,default=ROOT/"temp/timings.json");p.add_argument("--language",default="en");p.add_argument("--device",default="cpu",choices=["cpu","cuda","auto"]);a=p.parse_args()
 if not a.audio.is_file() or not a.lyrics.is_file():p.error("Audio stem or lyrics file is missing")
 lines=[x.strip() for x in a.lyrics.read_text(encoding="utf-8-sig").splitlines() if x.strip()]
 if not lines:p.error("lyrics.txt is empty")
 tokens=[(token,i) for i,line in enumerate(lines) for token in re.findall(r"\S+",line)]
 text=" ".join(token for token,_ in tokens)
 try:
  import torch,whisperx
  device=("cuda" if torch.cuda.is_available() else "cpu") if a.device=="auto" else a.device
  model,meta=whisperx.load_align_model(language_code=a.language,device=device)
  audio=whisperx.load_audio(str(a.audio))
  result=whisperx.align([{"start":0.0,"end":len(audio)/16000,"text":text}],model,meta,audio,device,return_char_alignments=False)
  aligned=[w for seg in result.get("segments",[]) for w in seg.get("words",[]) if w.get("start") is not None and w.get("end") is not None and w.get("word","").strip()]
  words=[]
  for idx,w in enumerate(aligned):
   _,line_index=tokens[idx] if idx<len(tokens) else (w.get("word","").strip(),0)
   words.append({"word":w["word"].strip(),"start":float(w["start"]),"end":float(w["end"]),"score":w.get("score"),"line_index":line_index})
  coverage=len(words)/max(1,len(tokens))
  payload={"method":"whisperx-forced-alignment","language":a.language,"expected_words":len(tokens),"aligned_words":len(words),"coverage":coverage,"words":words,"unmatched_count":max(0,len(tokens)-len(words))}
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
  validate_word_timings(words,len(tokens),.98)
  print(f"[align] {len(words)}/{len(tokens)} words aligned ({coverage:.1%})")
 except Exception as e:print(f"[alignment error] {e}",file=sys.stderr);raise SystemExit(1)
if __name__=="__main__":main()
