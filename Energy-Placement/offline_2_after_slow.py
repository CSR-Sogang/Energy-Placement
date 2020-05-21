import re

print "Be sure the unit of division is in Kilo or 32*Kilo or Mega"

MEGA = pow(1024,2)
PAGE_SIZE = 4096
# Consider only variables whose accessed volume is higher than THRESHOLD
#THRESHOLD = 100*MEGA
#THRESHOLD = MEGA
# Case of CG
THRESHOLD = PAGE_SIZE

f_hash_obj = open("HashValues", 'r')
f_size_obj = open("VarMinSize", 'r')
f_out = open("data.variable_access_pat", 'w')

f_out.write("Variable Information for Energy Calculation\n\n")

lines_hash = f_hash_obj.readlines()
lines_size = f_size_obj.readlines()

# mapping_obj_var[n] : N
#  -> n-th object's call-track hash value is N
mapping_obj_var = list()

line_num = len(lines_hash)
if line_num != len(lines_size):
  print "Baaam"

var_size = dict()
var_accessed = dict()
var_lifetime = dict()
var_rb_changed = dict()
var_cl_changed = dict()
var_llc_writeback = dict()
var_llc_writeback_incur = dict()

for i in range(line_num):
  tmp_hash = int(lines_hash[i].replace('\n',''))
  mapping_obj_var.append(tmp_hash)
  if tmp_hash not in var_size.keys():
    var_size[tmp_hash] = int(lines_size[i])
  else:
    var_size[tmp_hash] += int(lines_size[i])

"""
for i in mapping_obj_var:
  print i, '\t', var_size[i]
"""

"""
for i in mapping_obj_var:
  if i not in var_size.keys():
    print "Something is wrong"
"""

for i in var_size.keys():
  var_accessed[i] = 0
  var_rb_changed[i] = 0
  var_cl_changed[i] = 0
  var_lifetime[i] = 0
  var_llc_writeback[i] = 0
  var_llc_writeback_incur[i] = 0
  #print i, "\t", var_size[i]


f_in = open("result-all-major", 'r')

i = 0
flag_prof = 0

for line in f_in.readlines():

  if "accessed" in line:
    i = 0
    flag_prof = 1
    continue
  elif "selective" in line:
    i = 0
    flag_prof = 2
    continue
  elif "partial" in line:
    i = 0
    flag_prof = 3
    continue
  elif "writeback" in line:
    i = 0
    flag_prof = 4
    continue
  elif "incurred" in line:
    i = 0
    flag_prof = 5
    continue
  
  line = line.replace('\n','')

  if len(line.split('\t')) > 1:
    if flag_prof == 1 and i < len(mapping_obj_var):
      var_accessed[mapping_obj_var[i]] += int(line.split('\t')[1])
      #print i, mapping_obj_var[i]
    elif flag_prof == 2 and i < len(mapping_obj_var):
      var_rb_changed[mapping_obj_var[i]] += int(line.split('\t')[1])
      #print line.split('\t')
    elif flag_prof == 3 and i < len(mapping_obj_var):
      #print line.split('\t')
      var_cl_changed[mapping_obj_var[i]] += int(line.split('\t')[1])
    elif flag_prof == 4 and i < len(mapping_obj_var):
      var_llc_writeback[mapping_obj_var[i]] += int(line.split('\t')[1])
    elif flag_prof == 5 and i < len(mapping_obj_var):
      var_llc_writeback_incur[mapping_obj_var[i]] += int(line.split('\t')[1])

    i += 1


f_in.close()

for i in var_llc_writeback_incur.keys():
  print var_llc_writeback_incur[i]

#print fast_exetime

# Sort for following variable's accessed volume
hash_list = var_size.keys()
hash_list.sort(key=lambda x:var_accessed[x], reverse=True)

# Get a lifetime of variables to derive the REF energy of DRAM
f_in = open("timedat_fast_exe", 'r')
fast_exe = str()

for line in f_in.readlines():
  line = line.replace('\n','')
  if len(line.split()) >= 1 and line.split()[0] == 'real':
    fast_exe = line.split()[1]

f_in.close()

minute = int()
second = int()
time_info = re.findall(r'(.*)m(.*)s', fast_exe)
if len(time_info) >= 1 and len(time_info[0]) >= 2:
  minute = float(time_info[0][0])
  second = float(time_info[0][1])

# The execution time of fast pass
# Real lifetime is derived by multiplying normalized lifetime with fast_exetime
fast_exetime = minute*60+second


# To get all normalized lifetime of variables in slow pass
f_in = open("var_time_info", 'r')
flag_time = False

for line in f_in.readlines():
  line = line.replace('\n','')
  if "Normalized" in line:
    flag_time = True
    continue

  if flag_time == True and len(line.split()) == 3:
    hash_val = int(line.split()[1])
    var_lifetime[hash_val] = float(line.split()[2])
    

f_in.close()

# Write output data of post offline process
headline1 = "Hash value of Vars"
headline2 = "Size(B/4096)"
headline3 = "Accessed(B/4096)"
headline4 = "Lifetime(sec)"
headline5 = "Dirty RB(/4K)"
headline6 = "Dirty CL(/4K)"
headline7 = "LLC WrBack(/M)"
headline8 = "LLC WBIncur(/M)"

f_out.write(headline1.ljust(len(headline1)+5)+headline2.ljust(len(headline2)+2)+ \
headline3.ljust(len(headline3)+2)+headline4.ljust(len(headline4)+2)+ \
headline5.ljust(len(headline5)+2)+headline6.ljust(len(headline6)+2)+headline7.ljust(len(headline7)+2)+headline8+'\n')
for i in hash_list:
  if var_accessed[i] > THRESHOLD:
    size_str = str(var_size[i]/PAGE_SIZE)
    accessed_str = str(var_accessed[i]/PAGE_SIZE)
    lifetime_str = "%.2f" % (var_lifetime[i]*fast_exetime)
    rb_changed_str = str(var_rb_changed[i]/PAGE_SIZE)
    cl_changed_str = str(var_cl_changed[i]/PAGE_SIZE)
    #lifetime_str = str(int(var_lifetime[i]*fast_exetime))
    llc_writeback_str = str(var_llc_writeback[i]/MEGA)
    if float(var_llc_writeback[i]) / MEGA < 1.0:
      llc_writeback_str = "%.2f" % (float(var_llc_writeback[i])/MEGA)
    llc_writeback_incur_str = str(var_llc_writeback_incur[i]/MEGA)
    if float(var_llc_writeback_incur[i]) / MEGA < 1.0:
      llc_writeback_incur_str = "%.2f" % (float(var_llc_writeback_incur[i])/MEGA)
    

    """
    size_str = "%.2f" % (float(var_size[i]/64)/MEGA)
    accessed_str = "%.2f" % (float(var_accessed[i]/64)/MEGA)
    rb_changed_str = "%.2f" % (float(var_rb_changed[i]))
    cl_changed_str = "%.2f" % (float(var_cl_changed[i]))
    lifetime_str = "%.2f" % (var_lifetime[i]*fast_exetime)
    """

    f_out.write(str(i).ljust(len(headline1)+5)+size_str.ljust(len(headline2)+2)+\
    accessed_str.ljust(len(headline3)+2)+lifetime_str.ljust(len(headline4)+2)+\
    cl_changed_str.ljust(len(headline5)+2)+rb_changed_str.ljust(len(headline6)+2)+\
    llc_writeback_str.ljust(len(headline7)+2)+llc_writeback_incur_str+'\n')


f_hash_obj.close()
f_size_obj.close()
f_out.close()
