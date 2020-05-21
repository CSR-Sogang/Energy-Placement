
print "Be sure the unit of division is in Kilo or 32*Kilo or Mega"

KILO = 1024
MEGA = pow(1024, 2)
PAGE_SIZE = 4096
CACHELINE_SIZE = 64

Ed = {'ActPre':3.07, 'RdWr':1.19, 'Ref':0.35}
Es = {'ActPre':2.68, 'Rba':1, 'Wb':2.83}

Ed_var = dict()
Es_var_s = dict()
Es_var_p = dict()

#VarSize = []
#VarAccessedVolume = []
#VarDirtyBuffer = []
#VarDirtyCache = []

var_size = dict()
accessed_size = dict()
hash_list = list()

# Energy calculation requires variables' 
# (1)sizes, (2)accessed volumes, (3,4)dirty bit counts, (5)lifetime
f = open('data.variable_access_pat', 'r')
f_lt = open('var_time_info', 'r')
f_out1 = open('data.energy_selective','w')
f_out2 = open('data.energy_partial','w')
f_out = open("data.energy", 'w')

#lines = f.readlines()
#count = int(lines[0])
#print "count is", count
#flag = 0

for line in f.readlines():
  #print line.split('\t')
  line = line.replace('\n', '')

  # Headline starts from "Hash values of variables"
  # The others are all data
  # Variables' sizes and accessed sizes are written in KB unit
  if len(line.split()) == 8 and 'Hash' not in line.split()[0]:
    items = [float(i) for i in line.split()]
    hashval = int(line.split()[0])
    hash_list.append(hashval)

    Ed_var[hashval] = Ed['ActPre']*items[2] + Ed['RdWr']*items[2] + Ed['Ref']*items[1]*items[3]
    # Selective write energy of STTRAM
    #Es_var[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[3]/64
    # Partial write energy of STTRAM
    #Es_var[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[4]/THRESHOLD

    # Selective write
    Es_var_s[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[4]*PAGE_SIZE
    #Es_var_s[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[3]*64
    ##Es_var_s[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[3]*KILO
    ##Es_var_s[hashval] = Ed['ActPre']*items[2] + Ed['RdWr']*items[2] #+ Ed['Ref']*items[1]*29.09
    ##Es_var_s[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[4]
    # Partial write
    #Es_var_p[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[4]/CACHELINE_SIZE
    Es_var_p[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[5]
    #Es_var_p[hashval] = Es['ActPre']*items[2] + Es['Rba']*items[2] + Es['Wb']*items[4]*16

    var_size[hashval] = int(line.split()[1])
    accessed_size[hashval] = int(line.split()[2])


#f_out.write(str(hash_list)+'\n')
for i in hash_list:
  f_out1.write(str(i)+'\n')
  f_out2.write(str(i)+'\n')
  f_out.write(str(i)+'\n')

  #S_str = "%.2f\n" % (var_size[i]/KILO)

  # Variables' sizes and accessed sizes are written in MB unit
  #f_out.write(str(var_size[i]/MEGA)+'\n')

  # BFS, SF was done with KILO
  """
  if var_size[i]/KILO == 0:
    if float(var_size[i])/KILO > 0.5:
      f_out.write('1\n')
    else:
      f_out.write('0\n')
  else:
    f_out.write(str(var_size[i]/KILO)+'\n')
  """
  # CG was done with raw
  f_out.write(str(var_size[i])+'\n')

  # BFS, SF was done with KILO
  """
  if accessed_size[i]/KILO == 0:
    if float(accessed_size[i])/KILO >= 0.5:
      f_out.write('1\n')
    else:
      f_out.write('0\n')
  else:
    f_out.write(str(accessed_size[i]/KILO)+'\n')
  """
  # CG was done with raw
  f_out.write(str(accessed_size[i])+'\n')

  #Ed_str = "%.2f\n" % (Ed_var[i]/MEGA)
  #Ed_str = "%.2f\n" % (Ed_var[i]/(32*KILO))
  Ed_str = "%.2f\n" % (Ed_var[i]/KILO)
  f_out1.write(Ed_str)
  f_out2.write(Ed_str)
  f_out.write(Ed_str)

  #Es_str_s = "%.2f\n" % (Es_var_s[i]/MEGA)
  #Es_str_p = "%.2f\n" % (Es_var_p[i]/MEGA)
  #Es_str_s = "%.2f\n" % (Es_var_s[i]/(32*KILO))
  #Es_str_p = "%.2f\n" % (Es_var_p[i]/(32*KILO))
  Es_str_s = "%.2f\n" % (Es_var_s[i]/KILO)
  Es_str_p = "%.2f\n" % (Es_var_p[i]/KILO)
  f_out1.write(Es_str_s)
  f_out2.write(Es_str_p)
  f_out.write(Es_str_s)
  f_out.write(Es_str_p)


f.close()
f_lt.close()
f_out1.close()
f_out2.close()
f_out.close()
