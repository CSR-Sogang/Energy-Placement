f_in1 = open("data.variable_access_pat", 'r')
f_in2 = open("data.moca_variable_pat", 'r')
f_out1 = open("data.4k_cache", 'w')
f_out2 = open("data.20m_cache", 'w')
f_out3 = open("data.llc_mpki", 'w')

lines = f_in1.readlines()
lines_llc = f_in2.readlines()

for line in lines:
  line = line.replace('\n','')

  if len(line.split()) > 1:
    if "Variable" not in line.split()[0] and "Hash" not in line.split()[0]:
      f_out1.write(line.split()[4] + "\n")
      f_out2.write(line.split()[6] + "\n")

for line in lines_llc:
  line = line.replace('\n','')

  if len(line.split()) > 1:
    if "Hash" not in line.split()[0]:
      f_out3.write(line.split()[2] + '\n')

f_in1.close()
f_in2.close()
f_out1.close()
f_out2.close()
f_out3.close()
