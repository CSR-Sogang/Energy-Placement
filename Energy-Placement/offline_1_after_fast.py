#import heapq
import Queue
import math

f = open("var_time_info",'r')
hashF = open("HashValues", 'w')
sizeF = open("VarMinSize", 'w')

lineVar = f.readlines()[-3]
countVar = int(lineVar.split(':')[1])
f.close()

f = open("var_time_info",'r')

# In every iteration in for loop, object entry comes into hash queue and go out to size queue
hashObj = Queue.Queue()
sizeObj = Queue.Queue()
flagHero = dict()  # If an index is set, that index of variable is hero variable
sizeVar = dict()  # Key is variable's hash value

for i in f.readlines():
  if "[Hash]" in i:
    hashVal = int(i.split()[1])
    if not flagHero.has_key(hashVal):
      flagHero[hashVal] = False
      sizeVar[hashVal] = 0
    hashObj.put(hashVal)
    #set_hash.add(int(i.split()[1]))
  elif "[Trace]" in i and "size" in i:
    tmpHash, tmpSize = -1, -1
    if not hashObj.empty():
      tmpHash = hashObj.get()
    else:
      print "No [Hash] before [Trace]"
      continue
    
    for j in i.split():
      if len(j.split(':')) > 1:
        if j.split(':')[0] == "size":
          tmpSize = int(j.split(':')[1])
          #print tmpSize
          if tmpSize > 0:
            flagHero[tmpHash] = True
            #print tmpSize
            #print int(j.split(':')[1])
          sizeObj.put((tmpHash, tmpSize))
    #sizeObj.put(int((i.split()[4])[5:]))

  tmpTup = ()
  #if not hashObj.empty() and not sizeObj.empty():
  if not sizeObj.empty():
    tmpTup = sizeObj.get()
    #print tmpTup
    
    #if flagHero[tmpTup[0]]:
    sizeVar[tmpTup[0]] += tmpTup[1]

#for i in sizeVar.keys():
  #print i, "has", sizeVar[i], "size"
  #print "Hero or not :", flagHero[i]

# Sort variables' hash values with their total sizes
hashVar_sorted = sizeVar.keys()
hashVar_sorted.sort(key=lambda x:sizeVar[x], reverse=True)


f.close()

# Print the hash values and total volumes of variables
footprint = 0
obj_count = 0
stddev = 0
for i in hashVar_sorted:
  print i, '\t', sizeVar[i]
  footprint += sizeVar[i]
  obj_count += 1

average_size = float(footprint)/obj_count
print "Total footprint : ", footprint
print "Object count : ", obj_count
print "Average size : ", average_size

for i in hashVar_sorted:
  stddev += (sizeVar[i]-average_size)*(sizeVar[i]-average_size)

print "Standard Deviation : ", math.sqrt(stddev/obj_count)


hashObj_after = Queue.Queue()
sizeObj_after = Queue.Queue()

f = open("var_time_info",'r')

for i in f.readlines():
  if "[Hash]" in i:
    hashVal = int(i.split()[1])
    hashObj_after.put(hashVal)
    #set_hash.add(int(i.split()[1]))
  elif "[Trace]" in i and "size" in i:
    tmpHash, tmpSize = -1, -1
    if not hashObj_after.empty():
      tmpHash = hashObj_after.get()

      if sizeVar[tmpHash] < 0:
        continue
    else:
      print "No [Hash] before [Trace]"
      continue
    
    for j in i.split():
      if len(j.split(':')) > 1:
        if j.split(':')[0] == "size":
          tmpSize = int(j.split(':')[1])
          sizeObj_after.put((tmpHash, tmpSize))

  tmpTup = ()

  if not sizeObj_after.empty():
    tmpTup = sizeObj_after.get()
    #print tmpTup
    
    #if flagHero[tmpTup[0]]:
    hashF.write(str(tmpTup[0])+'\n')
    sizeF.write(str(tmpTup[1])+'\n')


f.close()
hashF.close()
sizeF.close()
