from PTF_Err import PTF_Err

def mut_pos_compare_appendid_res(sen1, sen2, temp_id):#sen2 is the add mask sen
  res = []
  for i in range(len(sen1.words)):
    # filter out the too close words
    if i == temp_id-1 or i == temp_id-2:
      continue
    if i < temp_id - 1:
      if sen1.words[i].upos != sen2.words[i].upos:
        res.append(PTF_Err(sen1.words[i].text, i+1, sen1.words[i].upos, sen2.words[i].upos))
    else:
      if sen1.words[i].upos != sen2.words[i+1].upos:
        res.append(PTF_Err(sen1.words[i].text, i+1, sen1.words[i].upos, sen2.words[i+1].upos))
  return res


def mut_pos_compare_appendid(sen1, sen2, temp_id):#sen2 is the add mask sen
  for i in range(len(sen1.words)):
    # filter out the too close words
    if i == temp_id-1 or i == temp_id-2:
      continue
    if i < temp_id - 1:
      if sen1.words[i].upos != sen2.words[i].upos:
        return False
    else:
      if sen1.words[i].upos != sen2.words[i+1].upos:
        return False
  return True


def mut_deprel_compare_appendid(sen1, sen2, temp_id):#sen2 is the add mask sen
  for i in range(len(sen1.words)):
    if i < temp_id - 1:
      # deprel equal
      if sen1.words[i].head == 0 and sen2.words[i].head != 0:
        return False
      elif sen1.words[sen1.words[i].head - 1].text != sen2.words[sen2.words[i].head - 1].text:
        return False
    else:
      if sen1.words[i].head == 0 and sen2.words[i+1].head != 0:
        return False
      elif sen1.words[sen1.words[i].head - 1].text != sen2.words[sen2.words[i+1].head - 1].text:
        return False
  return True


def mut_pos_compare_appendid_deprel_persent_res(sen1, sen2, temp_id):#sen2 is the add mask sen
  res = []
  deprel_right_num = 0
  for i in range(len(sen1.words)):
    # # filter out the too close words
    # if i == temp_id-1 or i == temp_id-2:
    #   continue
    if i < temp_id - 1:
      # pos equal
      if sen1.words[i].upos != sen2.words[i].upos:
        res.append(PTF_Err(sen1.words[i].text, i+1, sen1.words[i].upos, sen2.words[i].upos))
      # deprel equal
      if sen1.words[i].head == 0 and sen2.words[i].head == 0:
        deprel_right_num += 1
      elif sen1.words[sen1.words[i].head - 1].text == sen2.words[sen2.words[i].head - 1].text:
        deprel_right_num += 1
    else:
      if sen1.words[i].upos != sen2.words[i+1].upos:
        res.append(PTF_Err(sen1.words[i].text, i+1, sen1.words[i].upos, sen2.words[i+1].upos))
      if sen1.words[i].head == 0 and sen2.words[i+1].head == 0:
        deprel_right_num += 1
      elif sen1.words[sen1.words[i].head - 1].text == sen2.words[sen2.words[i+1].head - 1].text:
        deprel_right_num += 1
  if deprel_right_num/len(sen1.words) == 1:
    return res
  else:
    return []


def mut_pos_compare_withoutid_res(sen1, sen2, temp_id):
  res = []
  sen_length = len(sen1.words) if len(sen1.words) < len(sen2.words) else len(sen2.words)
  for i in range(sen_length):
    if sen1.words[i].upos != sen2.words[i].upos and sen1.words[i].id != temp_id:
      res.append((sen1.words[i].text, sen1.words[i].upos, sen2.words[i].upos))
  return res


def del_mut_pos_compare_res(sen1, sen2, delpart_id):#sen2 is the deled sen
  res = []
  sen_length = len(sen1.words)
  for i in range(sen_length):
    if i <= delpart_id[0]-2:
      if sen1.words[i].upos != sen2.words[i].upos:
        res.append(PTF_Err(sen1.words[i].text, i+1, sen1.words[i].upos, sen2.words[i].upos))
    if i >= delpart_id[1]:
      if sen1.words[i].upos != sen2.words[i-(delpart_id[1]-delpart_id[0]+1)].upos:
        res.append(PTF_Err(sen1.words[i].text, i+1, sen1.words[i].upos, sen2.words[i-(delpart_id[1]-delpart_id[0]+1)].upos))
  return res


def del_mut_pos_compare(sen1, sen2, delpart_id):#sen2 is the deled sen
  sen_length = len(sen1.words)
  for i in range(sen_length):
    if i <= delpart_id[0]-2:
      if sen1.words[i].upos != sen2.words[i].upos:
        return False
    if i >= delpart_id[1]:
      if sen1.words[i].upos != sen2.words[i-(delpart_id[1]-delpart_id[0]+1)].upos:
        return False
  return True


def mut_pos_compare_res(sen1, sen2):
  res = []
  dict1 = sen1.dict_for_compare()
  dict2 = sen2.dict_for_compare()
  for key in dict1.keys():
    if key in dict2:
      if dict1[key] != dict2[key]:
        res.append((key, dict1[key], dict2[key]))
  return res


def simple_compare_pos_deprel(sen1, sen2):
  sen_length = len(sen1.words)
  for i in range(sen_length):
    if sen1.words[i].upos != sen2.words[i].upos or sen1.words[i].head != sen2.words[i].head:
      return False
  return True


def simple_compare_pos(sen1, sen2):
  sen_length = len(sen1.words) if len(sen1.words) < len(sen2.words) else len(sen2.words)
  for i in range(sen_length):
    if sen1.words[i].upos != sen2.words[i].upos:
      return False
  return True


def simple_compare_pos_res(sen1, sen2):
  res = []
  sen_length = len(sen1.words) if len(sen1.words) < len(sen2.words) else len(sen2.words)
  for i in range(sen_length):
    if sen1.words[i].upos != sen2.words[i].upos:
      res.append((sen1.words[i].text, sen1.words[i].upos, sen2.words[i].upos))
  return res